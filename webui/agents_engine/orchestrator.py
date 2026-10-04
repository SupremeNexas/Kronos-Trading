import uuid
import logging
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from webui.agents_engine.checkpoint.manager import CheckpointManager
from webui.agents_engine.memory.manager import MemoryManager

# New Explicit Desk Imports
from webui.agents_engine.desks.research_desk import ResearchDesk
from webui.agents_engine.desks.forecast_desk import ForecastDesk
from webui.agents_engine.desks.portfolio_desk import PortfolioDesk
from webui.agents_engine.desks.validation_desk import ValidationDesk
from webui.agents_engine.desks.risk_desk import RiskDesk
from webui.agents_engine.desks.oversight_desk import OversightDesk
from webui.agents_engine.desks.execution_desk import ExecutionDesk

from webui.agents_engine.desk_schemas import (
    MarketSnapshot,
    ForecastDistribution,
    InvestmentView,
    PortfolioTarget,
    ValidationState,
    RiskDecision,
    ExecutionPlan,
    PaperOrderResult
)

logger = logging.getLogger(__name__)

class AgentEngineOrchestrator:
    """
    Main orchestrator for Kronos multi-agent execution pipelines conforming to AI Hedge Fund Research guide.
    Pipeline:
      - ResearchDesk -> MarketSnapshot
      - ForecastDesk -> ForecastDistribution
      - PortfolioDesk -> InvestmentView -> PortfolioTarget
      - ValidationDesk -> ValidationState
      - RiskDesk -> RiskDecision
      - ExecutionDesk -> ExecutionPlan (PENDING_CONFIRMATION) / PaperOrderResult
      - OversightDesk -> Advisory context
    """

    def __init__(self, broker, predictor=None, db_path: str = None, memory_path: str = None):
        self.broker = broker
        self.predictor = predictor

        # Internal managers
        self.checkpoint_mgr = CheckpointManager()
        self.memory_mgr = MemoryManager(memory_path=memory_path)

        # Explicit Desks
        self.research_desk = ResearchDesk()
        self.forecast_desk = ForecastDesk(predictor=self.predictor)
        # Portfolios and Risk desks will get realistic cash balances below
        self.portfolio_desk = PortfolioDesk()
        self.validation_desk = ValidationDesk()
        self.risk_desk = RiskDesk()
        self.oversight_desk = OversightDesk()
        self.execution_desk = ExecutionDesk(broker_client=self.broker)

        # Quant validation and trading journal (lazy-loaded)
        self._trading_journal = None

    @property
    def trading_journal(self):
        if self._trading_journal is None:
            from webui.agents_engine.trading_journal import TradingJournal
            self._trading_journal = TradingJournal()
        return self._trading_journal

    def confirm_trade(self, entry_id: str, confirm: bool) -> Dict[str, Any]:
        """User explicitly confirmed or rejected the pending trade."""
        success = self.trading_journal.update_confirmation(entry_id, confirm)
        if not success:
            return {"success": False, "error": "Journal entry not found."}

        if not confirm:
            self.trading_journal.update_order(entry_id, None, "REJECTED_BY_USER", 0)
            return {"success": True, "executed": False, "status": "REJECTED"}

        # Parse the journal to re-obtain order instructions
        entry = None
        data = self.trading_journal._read()
        for i in data.get("entries", []):
            if i["id"] == entry_id:
                entry = i
                break

        if not entry:
            return {"success": False, "error": "Journal entry lost."}

        execution_plan_dict = entry.get("execution_plan", {})
        if not execution_plan_dict:
            # Fallback for old schema
            symbol = entry["symbol"]
            action = entry.get("prediction_decision", entry.get("signal", "HOLD"))
            qty = entry.get("position_sizing", {}).get("position_size", 0)
            price_target = entry.get("forecast", {}).get("target_price", 0)
            plan = ExecutionPlan(
                symbol=symbol,
                side=action,
                quantity=qty,
                price_target=price_target,
                validation_status="PASS",
                risk_status="ALLOW",
                proposal_timestamp=datetime.datetime.now()
            )
        else:
            plan = ExecutionPlan(**execution_plan_dict)

        result = self.execution_desk.execute_paper(plan, force_confirm=True)

        if result.status == "FILLED":
            self.trading_journal.update_order(entry_id, result.order_id, "FILLED", result.filled_price)
            # Log exact paper execution
            return {"success": True, "executed": True, "status": "FILLED", "order_id": result.order_id}
        else:
            self.trading_journal.update_order(entry_id, None, f"FAILED: {result.error}", 0)
            return {"success": False, "error": result.error}

    def run_cycle(
        self,
        symbol: str,
        timeframe: str = "1d",
        pred_len: int = 14,
        allow_trading: bool = True,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a single workflow cycle via explicit Quant Desks. Returns overall result.
        """
        if not analysis_id:
            analysis_id = f"run_desk_{uuid.uuid4().hex[:12]}_{datetime.datetime.now().strftime('%Y%p%d_%H%M%S')}"

        logger.info(f"Starting Explicit Quant Desk cycle {analysis_id} for symbol {symbol}")

        flow_data = {
            "analysis_id": analysis_id,
            "symbol": symbol,
            "timeframe": timeframe,
        }

        # Setup cash balances dynamically
        portfolio_cash = self.broker.get_balance() if hasattr(self.broker, "get_balance") else 100000.0
        portfolio_holdings = self.broker.get_positions() if hasattr(self.broker, "get_positions") else {}
        self.portfolio_desk = PortfolioDesk(cash_balance=portfolio_cash, current_positions=portfolio_holdings)
        self.risk_desk = RiskDesk(cash_balance=portfolio_cash)

        # STAGE 1: ResearchDesk
        stage = "RESEARCH"
        self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
        try:
            snapshot = self.research_desk.get_snapshot(symbol, timeframe)
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=snapshot.model_dump(mode='json'))
        except Exception as e:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
            return {"success": False, "stage": stage, "error": str(e)}

        flow_data["research"] = snapshot.model_dump(mode='json')
        flow_data["current_price"] = snapshot.current_price

        if snapshot.data_quality != "GOOD":
            return {"success": False, "stage": stage, "error": "No price data retrieved or insufficient quality."}

        # STAGE 2: ForecastDesk
        stage = "FORECAST"
        self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
        try:
            forecast = self.forecast_desk.forecast(symbol, timeframe, snapshot, pred_len)
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=forecast.model_dump(mode='json'))
        except Exception as e:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
            return {"success": False, "stage": stage, "error": str(e)}

        flow_data["forecast"] = forecast.model_dump(mode='json')

        # STAGE 3: PortfolioDesk
        stage = "PORTFOLIO"
        self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
        try:
            view = self.portfolio_desk.get_view(forecast)
            target = self.portfolio_desk.optimize(view, forecast)
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result={"view": view.model_dump(mode='json'), "target": target.model_dump(mode='json')})
        except Exception as e:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
            return {"success": False, "stage": stage, "error": str(e)}

        flow_data["decision"] = view.model_dump(mode='json') # map to old decision output for frontend partially
        flow_data["target"] = target.model_dump(mode='json')

        if view.signal in ["WAIT", "NO_TRADE", "HOLD"] or target.target_weight == 0:
            flow_data["execution"] = {"status": view.signal, "reason": "Portfolio optimization skipped trade."}
            return self._finalize_and_log(flow_data, forecast, view, target, None, None, None, snapshot)

        # STAGE 4: ValidationDesk
        stage = "VALIDATION"
        self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
        try:
            validation = self.validation_desk.validate(target, forecast)
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=validation.model_dump(mode='json'))
        except Exception as e:
            logger.error(f"Quant validation error: {e}")
            validation = ValidationState(status="FAIL", metrics={}, reasons=[str(e)])
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))

        flow_data["quant_validation"] = validation.model_dump(mode='json')

        if validation.status in ["FAIL", "INSUFFICIENT_DATA"]:
            flow_data["execution"] = {"status": "NO_TRADE", "reason": f"Blocked by Quant Gates: {validation.reasons}"}
            return self._finalize_and_log(flow_data, forecast, view, target, validation, None, None, snapshot)

        # STAGE 5: RiskDesk
        stage = "RISK"
        self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
        try:
            risk = self.risk_desk.evaluate(target, validation, current_holdings=portfolio_holdings)
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=risk.model_dump(mode='json'))
        except Exception as e:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
            return {"success": False, "stage": stage, "error": str(e)}

        flow_data["risk_validation"] = risk.model_dump(mode='json')

        if risk.status == "BLOCK" or risk.adjusted_quantity <= 0:
            flow_data["execution"] = {"status": "NO_TRADE", "reason": f"Risk checks failed or quantity 0. {risk.reasons}"}
            return self._finalize_and_log(flow_data, forecast, view, target, validation, risk, None, snapshot)

        # STAGE 6: OversightDesk
        stage = "OVERSIGHT"
        try:
            oversight = self.oversight_desk.review_cycle(forecast, view, validation, risk)
            flow_data["decision"].update(oversight) # merge into decision for frontend
        except Exception as e:
            logger.warning(f"Oversight skipped: {e}")

        # STAGE 7: ExecutionDesk - PENDING_CONFIRMATION
        plan = self.execution_desk.create_plan(target, risk, validation.status)
        order_result = self.execution_desk.execute_paper(plan, force_confirm=False)

        flow_data["execution_plan"] = plan.model_dump(mode='json')
        flow_data["execution"] = {
            "status": order_result.status,
            "reason": order_result.error or f"Required by protocol. Setup for {plan.quantity} {symbol}",
            "order_info": {
                "symbol": plan.symbol,
                "side": plan.side,
                "quantity": plan.quantity,
                "price": plan.price_target
            }
        }

        return self._finalize_and_log(flow_data, forecast, view, target, validation, risk, plan, snapshot)

    def _finalize_and_log(
        self,
        flow_data: Dict[str, Any],
        forecast: ForecastDistribution,
        view: InvestmentView,
        target: PortfolioTarget,
        validation: Optional[ValidationState],
        risk: Optional[RiskDecision],
        plan: Optional[ExecutionPlan],
        snapshot: MarketSnapshot
    ) -> Dict[str, Any]:
        """Saves journal entry explicitly conforming to the hedge fund schema."""
        try:
            # We map explicit schemas back to the previous JSON schema for frontend compatibility
            # while fully storing the new explicit dicts inside the entry context

            # Legacy expected mappings for TradingJournal.record_prediction
            q_val = None
            if validation:
                q_val = {
                    "all_gates_passed": validation.status in ["PASS", "WARN"],
                    "verdict": validation.status,
                    "metrics": validation.metrics,
                    "reasons": validation.reasons,
                    "position_sizing": {
                        "approved": (risk.status != "BLOCK") if risk else False,
                        "position_size": plan.quantity if plan else 0.0
                    }
                }

            r_val = None
            if risk:
                r_val = {
                    "approved": risk.status != "BLOCK",
                    "adjusted_quantity": risk.adjusted_quantity,
                    "reasons": risk.reasons
                }

            journal_id = self.trading_journal.record_prediction(
                symbol=flow_data["symbol"],
                market_data_timestamp=snapshot.timestamp.isoformat(),
                forecast={
                    "direction": view.signal,
                    "expected_return_pct": forecast.expected_return_pct,
                    "target_price": forecast.expected_return_pct * snapshot.current_price + snapshot.current_price,
                    "support": forecast.lower_range,
                    "resistance": forecast.upper_range,
                    "model": forecast.forecast_model
                },
                confidence=forecast.confidence,
                signal=view.signal,
                validation_results=q_val,
                risk_result=r_val,
                position_sizing=q_val.get("position_sizing") if q_val else None
            )
            flow_data["journal_id"] = journal_id

            # Post-patch update to journal to write explicit detailed info
            data = self.trading_journal._read()
            for entry in data["entries"]:
                if entry["id"] == journal_id:
                    entry["evidence"] = {
                        "supporting_evidence": view.supporting_evidence,
                        "opposing_evidence": view.opposing_evidence,
                        "missing_information": "",
                        "conditions_that_would_change_decision": view.decision_changing_conditions
                    }
                    entry["prediction_decision"] = view.signal
                    entry["execution_plan"] = plan.model_dump(mode='json') if plan else None
                    entry["portfolio_target"] = target.model_dump(mode='json') if target else None
                    self.trading_journal._write(data)
                    break
        except Exception as e:
            logger.error(f"Trading journal record error: {e}")

        flow_data["success"] = True
        return flow_data
