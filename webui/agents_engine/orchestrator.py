import uuid
import logging
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from webui.agents_engine.checkpoint.manager import CheckpointManager
from webui.agents_engine.memory.manager import MemoryManager
from webui.agents_engine.gate.risk_gate import KronosRiskGate
from webui.agents_engine.llm_agent import KronosLLMAgent
from webui.data_fetcher import fetch_symbol_data

logger = logging.getLogger(__name__)

class AgentEngineOrchestrator:
    """
    Main orchestrator for Kronos multi-agent execution pipelines.
    Runs structured stages sequentially:
      - Resolve outcomes of pending trades (Self-Reflection)
      - Fetch data
      - Forecast using Kronos model
      - LLM agent synthesis
      - Hard Risk Gate verification
      - Trade execution
    Supports state checkpointing & resuming.
    """

    def __init__(self, broker, predictor=None, db_path: str = None, memory_path: str = None):
        self.broker = broker
        self.predictor = predictor

        # Internal managers
        self.checkpoint_mgr = CheckpointManager()  # Uses defaults
        self.memory_mgr = MemoryManager(memory_path=memory_path)
        self.risk_gate = KronosRiskGate()
        self.llm_agent = KronosLLMAgent()

    def run_cycle(
        self,
        symbol: str,
        timeframe: str = "1d",
        pred_len: int = 14,
        allow_trading: bool = True,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a single workflow cycle. Returns overall result.
        """
        if not analysis_id:
            # Create a execution run ID
            analysis_id = f"run_{uuid.uuid4().hex[:12]}_{datetime.datetime.now().strftime('%Y%p%d_%H%M%S')}"

        logger.info(f"Starting Kronos cycle {analysis_id} for symbol {symbol}")

        # STAGE 0: Self-Reflection / Node outcome verification
        # Query current price first to settle past unresolved trades
        current_price = self._resolve_past_trades(symbol, timeframe)

        flow_data = {
            "analysis_id": analysis_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price
        }

        # STAGE 1: Data Fetching
        stage = "DATA_FETCH"
        checkpoint = self.checkpoint_mgr.get_checkpoint(analysis_id, stage)
        if checkpoint and checkpoint.get("status") == "SUCCESS":
            logger.info("Resuming stage DATA_FETCH from cache checkpoint.")
            data_result = checkpoint["result"]
        else:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
            try:
                df = fetch_symbol_data(symbol, timeframe)
                if df.empty or len(df) < 50:
                    raise ValueError(f"Insufficient or empty data returned for {symbol}. Rows: {len(df)}")

                # We save summary representation in checkpoint
                data_result = {
                    "last_close": float(df['close'].iloc[-1]),
                    "record_count": len(df),
                    "file_path_represented": f"live_fetch_{symbol}_{timeframe}"
                }
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=data_result)
            except Exception as e:
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
                return {"success": False, "analysis_id": analysis_id, "stage": stage, "error": str(e)}

        # Update last price in flow data if fetched successfully
        if "last_close" in data_result:
            flow_data["current_price"] = data_result["last_close"]

        # STAGE 2: Quantitative Forecasting (Kronos)
        stage = "FORECAST"
        checkpoint = self.checkpoint_mgr.get_checkpoint(analysis_id, stage)
        if checkpoint and checkpoint.get("status") == "SUCCESS":
            logger.info("Resuming stage FORECAST from cache checkpoint.")
            forecast_result = checkpoint["result"]
        else:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
            try:
                # Re-fetch or pass data to prediction sequence
                df = fetch_symbol_data(symbol, timeframe)
                # Compute predictions using predictor model if loaded
                pred_metrics = self._calculate_predictions(df, symbol, pred_len)
                forecast_result = pred_metrics
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=forecast_result)
            except Exception as e:
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
                return {"success": False, "analysis_id": analysis_id, "stage": stage, "error": str(e)}

        flow_data["forecast"] = forecast_result

        # STAGE 3: Cognitive LLM Agent Analysis
        stage = "LLM_ANALYSIS"
        checkpoint = self.checkpoint_mgr.get_checkpoint(analysis_id, stage)
        if checkpoint and checkpoint.get("status") == "SUCCESS":
            logger.info("Resuming stage LLM_ANALYSIS from cache checkpoint.")
            llm_result = checkpoint["result"]
        else:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
            try:
                # Retrieve past feedback/memory lessons
                reflections = self.memory_mgr.get_past_reflections(symbol, limit=3)
                # Analyze opportunities
                analysis = self.llm_agent.analyze(
                    symbol=symbol,
                    current_price=flow_data["current_price"],
                    kronos_prediction=flow_data["forecast"],
                    past_reflections=reflections
                )
                llm_result = analysis
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=llm_result)
            except Exception as e:
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
                return {"success": False, "analysis_id": analysis_id, "stage": stage, "error": str(e)}

        flow_data["proposal"] = llm_result

        # STAGE 4: Risk Gate Verification
        stage = "RISK_GATE"
        checkpoint = self.checkpoint_mgr.get_checkpoint(analysis_id, stage)
        if checkpoint and checkpoint.get("status") == "SUCCESS":
            logger.info("Resuming stage RISK_GATE from cache checkpoint.")
            risk_result = checkpoint["result"]
        else:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
            try:
                portfolio_cash = self.broker.get_balance()
                portfolio_holdings = self.broker.get_positions()

                # Check proposing order size logic (default is 10% of portfolio buying power if buy)
                price = flow_data["current_price"]
                action = flow_data["proposal"].get("action", "HOLD")

                # Sizing suggestion logic depending on LLM agent confidence
                confidence = flow_data["proposal"].get("confidence", 0.5)
                # Max target size: scale with confidence
                target_allocation_pct = 0.20 * confidence # max 20% allocation

                if action == "BUY":
                    quantity = (portfolio_cash * target_allocation_pct) / price
                    # round to assets specs or 4 decimal points
                    quantity = float(round(quantity, 4))
                elif action == "SELL":
                    quantity = portfolio_holdings.get(symbol, {}).get("quantity", 0.0)
                else:
                    quantity = 0.0

                validation = self.risk_gate.validate_action(
                    symbol=symbol,
                    action=action,
                    price=price,
                    quantity=quantity,
                    stop_loss=flow_data["proposal"].get("stop_loss", 0.0),
                    take_profit=flow_data["proposal"].get("take_profit", 0.0),
                    portfolio_cash=portfolio_cash,
                    portfolio_holdings=portfolio_holdings
                )
                risk_result = validation
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=risk_result)
            except Exception as e:
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
                return {"success": False, "analysis_id": analysis_id, "stage": stage, "error": str(e)}

        flow_data["validation"] = risk_result

        # STAGE 5: Order Execution (Actionable Node)
        stage = "EXECUTION"
        checkpoint = self.checkpoint_mgr.get_checkpoint(analysis_id, stage)
        if checkpoint and checkpoint.get("status") == "SUCCESS":
            logger.info("Resuming stage EXECUTION from cache checkpoint.")
            exec_result = checkpoint["result"]
        else:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
            try:
                exec_result = {"executed": False, "order_info": None, "reason": "Execution skipped / disallowed"}

                approved = flow_data["validation"].get("approved", False)
                final_qty = flow_data["validation"].get("adjusted_quantity", 0.0)
                action = flow_data["proposal"].get("action", "HOLD")

                if approved and final_qty > 0.0 and allow_trading and action in ["BUY", "SELL"]:
                    order = self.broker.place_order(
                        symbol=symbol,
                        side=action,
                        quantity=final_qty,
                        price=flow_data["current_price"]
                    )
                    exec_result = {
                        "executed": order.get("success", False),
                        "order_info": order,
                        "reason": order.get("message", "Order placed successfully")
                    }

                    # STAGE 6: Memorization of Trading Decisions
                    # Save to Memory log so it can be evaluated/resolved on next cycle
                    self.memory_mgr.store_decision(
                        symbol=symbol,
                        ai_decision=flow_data["proposal"],
                        kronos_direction=flow_data["forecast"].get("signal", "HOLD"),
                        risk_level="MEDIUM",
                        entry_price=flow_data["current_price"]
                    )
                else:
                    exec_result["reason"] = f"Execution blocked. Gate Approved: {approved}, Adjusted Qty: {final_qty}"

                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=exec_result)
            except Exception as e:
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
                return {"success": False, "analysis_id": analysis_id, "stage": stage, "error": str(e)}

        flow_data["execution"] = exec_result

        # Clear checkpoint history for active run on total completion
        self.checkpoint_mgr.clear_checkpoints(analysis_id)

        return {
            "success": True,
            "analysis_id": analysis_id,
            "current_price": flow_data["current_price"],
            "forecast": flow_data["forecast"],
            "proposal": flow_data["proposal"],
            "validation": flow_data["validation"],
            "execution": flow_data["execution"]
        }

    def _resolve_past_trades(self, symbol: str, timeframe: str) -> float:
        """Helper to resolve previous unresolved trades and gather current asset price."""
        try:
            df = fetch_symbol_data(symbol, timeframe)
            if not df.empty:
                current_price = float(df['close'].iloc[-1])
                # Call memory manager to resolve outcomes
                self.memory_mgr.resolve_outcomes(symbol, current_price)
                return current_price
        except Exception as e:
            logger.error(f"Error fetching current price during self-reflection: {e}")

        # Hard fallback value of price
        positions = self.broker.get_positions()
        if symbol in positions:
            return float(positions[symbol].get("current_price", 100.0))
        return 100.0

    def _calculate_predictions(self, df: pd.DataFrame, symbol: str, pred_len: int) -> Dict[str, Any]:
        """Calculates prediction indicators based on live data or predictor model."""
        import numpy as np

        if self.predictor is not None:
            # We align with context length
            lookback = min(len(df) - 1, 400)
            x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume']]
            x_timestamp = df.iloc[-lookback:]['timestamps']

            # Calculate predicted future timestamps
            last_ts = x_timestamp.iloc[-1]
            time_diff = df['timestamps'].iloc[-1] - df['timestamps'].iloc[-2] if len(df) > 1 else pd.Timedelta(hours=1)
            future_ts = pd.date_range(start=last_ts + time_diff, periods=pred_len, freq=time_diff)

            from webui.app import MODEL_AVAILABLE
            if MODEL_AVAILABLE:
                pred_df = self.predictor.predict(
                    df=x_df,
                    x_timestamp=pd.Series(x_timestamp.reset_index(drop=True)),
                    y_timestamp=pd.Series(future_ts),
                    pred_len=pred_len,
                    T=1.0,
                    top_p=0.9,
                    sample_count=1
                )
            else:
                pred_df = self._simulate_predictions(df, pred_len)
        else:
            pred_df = self._simulate_predictions(df, pred_len)

        last_close = df['close'].iloc[-1]
        pred_closes = pred_df['close'].tolist()
        net_change = (pred_closes[-1] - last_close) / last_close

        signal = "HOLD"
        sl = last_close * 0.99
        tp = last_close * 1.03

        if net_change > 0.015:
            signal = "BUY"
            tp = max(pred_closes)
        elif net_change < -0.015:
            signal = "SELL"
            sl = max(pred_closes)
            tp = min(pred_closes)

        return {
            "signal": signal,
            "return_pct": float(round(net_change * 100, 2)),
            "support": float(round(min(pred_df['low']), 2)),
            "resistance": float(round(max(pred_df['high']), 2)),
            "last_close": float(round(last_close, 2))
        }

    def _simulate_predictions(self, df: pd.DataFrame, pred_len: int) -> pd.DataFrame:
        """Simulates price charts when the ML model predictor is empty/inactive."""
        import numpy as np
        last_close = df['close'].iloc[-1]
        sim_closes = last_close * (1.0 + np.cumsum(np.random.normal(0.0001, 0.0018, pred_len)))
        return pd.DataFrame({
            'open': sim_closes,
            'high': sim_closes * 1.002,
            'low': sim_closes * 0.998,
            'close': sim_closes,
            'volume': np.random.randint(10, 100, pred_len)
        })
