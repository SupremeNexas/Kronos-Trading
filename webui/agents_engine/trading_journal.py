"""
Kronos Trading Journal
======================
Persists every prediction, validation, and trade decision
to enable post-hoc analysis of model accuracy.
"""

import os
import json
import uuid
import datetime
import logging
from typing import Dict, Any, List, Optional
from webui.db import get_db_connection, _adapt_query

logger = logging.getLogger(__name__)

JOURNAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
JOURNAL_FILE = os.path.join(JOURNAL_DIR, "trading_journal.json")
os.makedirs(JOURNAL_DIR, exist_ok=True)


class TradingJournal:
    """
    Structured trading journal persisting every step of the pipeline to SQLite/PostgreSQL
    and fallback/legacy JSON.
    """

    def __init__(self, journal_path: str = None):
        self.journal_path = journal_path or JOURNAL_FILE
        self._init_journal()

    def _init_journal(self):
        if not os.path.exists(self.journal_path):
            self._write({"entries": []})

    def _read(self) -> Dict:
        try:
            with open(self.journal_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {"entries": []}

    def _write(self, data: Dict):
        try:
            with open(self.journal_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to write trading journal: {e}")

    def record_prediction(self,
                          symbol: str,
                          market_data_timestamp: str,
                          forecast: Dict[str, Any],
                          confidence: float,
                          signal: str,
                          validation_results: Optional[Dict[str, Any]] = None,
                          risk_result: Optional[Dict[str, Any]] = None,
                          position_sizing: Optional[Dict[str, Any]] = None) -> str:
        """
        Record a new prediction/signal entry. Returns the journal entry ID.
        """
        entry_id = f"jrn_{uuid.uuid4().hex[:12]}"
        run_id = f"run_{uuid.uuid4().hex[:12]}"

        # Base JSON
        entry = {
            "id": entry_id,
            "created_at": datetime.datetime.now().isoformat(),
            "market_data_timestamp": market_data_timestamp,
            "symbol": symbol.upper(),
            "forecast": {
                "direction": forecast.get("direction", "UNKNOWN"),
                "expected_return_pct": forecast.get("expected_return_pct", forecast.get("return_pct", 0.0)),
                "target_price": forecast.get("target_price", 0.0),
                "support": forecast.get("support", 0.0),
                "resistance": forecast.get("resistance", 0.0),
                "model": forecast.get("model", "KRONOS"),
                "horizon": forecast.get("horizon", 0)
            },
            "confidence": round(confidence, 3),
            "signal": signal.upper(),
            "validation": {
                "verdict": validation_results.get("verdict", "NOT_EVALUATED") if validation_results else "NOT_EVALUATED",
                "all_gates_passed": validation_results.get("all_gates_passed", False) if validation_results else False,
                "gates": validation_results.get("gates", {}) if validation_results else {},
            },
            "risk_result": risk_result or {},
            "position_sizing": position_sizing or {},
            "user_confirmation": "PENDING",
            "paper_order_id": None,
            "order_status": None,
            "fill_price": None,
            "exit_price": None,
            "outcome": "PENDING",
            "pnl_pct": None,
            "model_correct": None,
            "notes": ""
        }

        data = self._read()
        data["entries"].append(entry)
        if len(data["entries"]) > 1000:
            data["entries"] = data["entries"][-1000:]
        self._write(data)

        # SQL DB Persistence
        conn, db_type = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(_adapt_query("""
                INSERT INTO prediction_runs (
                    id, run_id, symbol, timeframe, forecast_horizon,
                    model_name, model_version, forecast_direction, expected_return,
                    predicted_target, lower_bound, upper_bound, confidence,
                    decision, validation_status, risk_status, data_timestamp,
                    supporting_evidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), (
                forecast.get("forecast_id", entry_id), run_id, symbol.upper(), "1D", forecast.get("horizon", 14),
                forecast.get("model", "KRONOS"), forecast.get("model_version", "Kronos-small-v1"), forecast.get("direction", "UNKNOWN"), 
                forecast.get("expected_return_pct", 0.0), forecast.get("target_price", 0.0),
                forecast.get("support", 0.0), forecast.get("resistance", 0.0), confidence,
                signal.upper(), validation_results.get("verdict", "") if validation_results else "",
                risk_result.get("status", "") if risk_result else "", forecast.get("data_timestamp", market_data_timestamp),
                forecast.get("inference_timestamp", "")
            ))
            
            # also insert event
            cursor.execute(_adapt_query("""
                INSERT INTO trading_events (id, run_id, symbol, stage, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """), (str(uuid.uuid4()), run_id, symbol.upper(), "PREDICTION", "CREATED", "{}"))

            conn.commit()
        except Exception as e:
            logger.error(f"DB Error writing prediction: {e}")
        finally:
            conn.close()

        return entry_id

    def update_confirmation(self, entry_id: str, confirmed: bool) -> bool:
        """Update user confirmation status."""
        data = self._read()
        for entry in data["entries"]:
            if entry["id"] == entry_id:
                entry["user_confirmation"] = "CONFIRMED" if confirmed else "REJECTED"
                entry["confirmation_at"] = datetime.datetime.now().isoformat()
                self._write(data)
                
                # SQL update
                conn, _ = get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(_adapt_query("UPDATE trade_proposals SET confirmation_state = ? WHERE prediction_id = ?"), 
                                  ("CONFIRMED" if confirmed else "REJECTED", entry_id))
                    # insert event
                    cursor.execute(_adapt_query("""
                        INSERT INTO trading_events (id, run_id, symbol, stage, status, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """), (str(uuid.uuid4()), entry_id, entry["symbol"], "CONFIRMATION", "CONFIRMED" if confirmed else "REJECTED", "{}"))
                    conn.commit()
                except Exception:
                    pass
                finally:
                    conn.close()
                return True
        return False

    def update_order(self, entry_id: str, order_id: str, order_status: str,
                     fill_price: float = None) -> bool:
        """Update order placement details."""
        data = self._read()
        for entry in data["entries"]:
            if entry["id"] == entry_id:
                entry["paper_order_id"] = order_id
                entry["order_status"] = order_status
                entry["fill_price"] = fill_price
                entry["order_updated_at"] = datetime.datetime.now().isoformat()
                self._write(data)
                
                # Update DB
                conn, _ = get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(_adapt_query("""
                        INSERT INTO paper_orders (id, trade_id, alpaca_order_id, order_status, actual_fill_price)
                        VALUES (?, ?, ?, ?, ?)
                    """), (str(uuid.uuid4()), entry_id, order_id, order_status, fill_price))
                    
                    cursor.execute(_adapt_query("""
                        INSERT INTO trading_events (id, run_id, symbol, stage, status, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """), (str(uuid.uuid4()), entry_id, entry["symbol"], "ORDER", order_status, "{}"))
                    conn.commit()
                except Exception:
                    pass
                finally:
                    conn.close()
                
                return True
        return False

    def update_outcome(self, entry_id: str, exit_price: float,
                       notes: str = "") -> bool:
        """
        Record the trade outcome. Determines if model was correct.
        """
        data = self._read()
        for entry in data["entries"]:
            if entry["id"] == entry_id:
                fill = entry.get("fill_price") or entry.get("forecast", {}).get("target_price", 0)
                signal = entry.get("signal", "HOLD")

                if fill and fill > 0 and exit_price > 0:
                    if signal in ["BUY", "BULLISH"]:
                        pnl_pct = ((exit_price - fill) / fill) * 100
                    elif signal in ["SELL", "BEARISH"]:
                        pnl_pct = ((fill - exit_price) / fill) * 100
                    else:
                        pnl_pct = 0.0
                else:
                    pnl_pct = 0.0

                entry["exit_price"] = exit_price
                entry["pnl_pct"] = round(pnl_pct, 2)
                entry["outcome"] = "PROFIT" if pnl_pct > 0 else ("LOSS" if pnl_pct < 0 else "BREAKEVEN")
                entry["notes"] = notes
                entry["resolved_at"] = datetime.datetime.now().isoformat()

                # Was the model directionally correct?
                forecast_dir = entry.get("forecast", {}).get("direction", "")
                actual_dir = "BULLISH" if exit_price > fill else ("BEARISH" if exit_price < fill else "NEUTRAL")
                entry["model_correct"] = (
                    (forecast_dir in ["BULLISH", "BUY"] and actual_dir == "BULLISH") or
                    (forecast_dir in ["BEARISH", "SELL"] and actual_dir == "BEARISH") or
                    (forecast_dir in ["NEUTRAL", "HOLD"] and actual_dir == "NEUTRAL")
                )

                self._write(data)
                
                # update prediction_outcomes
                conn, _ = get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(_adapt_query("""
                        INSERT INTO prediction_outcomes (id, prediction_id, actual_price, actual_return, direction_correct, prediction_outcome)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """), (str(uuid.uuid4()), entry_id, exit_price, pnl_pct, 1 if entry["model_correct"] else 0, entry["outcome"]))
                    conn.commit()
                except Exception:
                    pass
                finally:
                    conn.close()

                return True
        return False

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a single journal entry by ID."""
        data = self._read()
        for entry in data["entries"]:
            if entry["id"] == entry_id:
                return entry
        return None

    def get_entries(self, symbol: str = None, limit: int = 50,
                    outcome: str = None) -> List[Dict[str, Any]]:
        """Query journal entries with optional filters."""
        data = self._read()
        entries = data.get("entries", [])

        if symbol:
            entries = [e for e in entries if e["symbol"] == symbol.upper()]
        if outcome:
            entries = [e for e in entries if e["outcome"] == outcome.upper()]

        return entries[-limit:]

    def get_accuracy_report(self, symbol: str = None) -> Dict[str, Any]:
        """
        Answer: Was the model actually right?
        Comprehensive accuracy report across all resolved entries.
        """
        data = self._read()
        entries = data.get("entries", [])

        if symbol:
            entries = [e for e in entries if e["symbol"] == symbol.upper()]

        resolved = [e for e in entries if e["outcome"] not in ["PENDING", None]]
        if not resolved:
            return {
                "total_predictions": len(entries),
                "resolved": 0,
                "message": "No resolved trades to analyze"
            }

        total = len(resolved)
        correct = sum(1 for e in resolved if e.get("model_correct", False))
        profits = sum(1 for e in resolved if e["outcome"] == "PROFIT")
        losses = sum(1 for e in resolved if e["outcome"] == "LOSS")
        breakeven = sum(1 for e in resolved if e["outcome"] == "BREAKEVEN")

        pnls = [e.get("pnl_pct", 0) for e in resolved if e.get("pnl_pct") is not None]
        avg_pnl = sum(pnls) / len(pnls) if pnls else 0

        confirmed_trades = [e for e in resolved if e.get("user_confirmation") == "CONFIRMED"]
        rejected_trades = [e for e in entries if e.get("user_confirmation") == "REJECTED"]
        no_trade_entries = [e for e in entries if e.get("validation", {}).get("verdict") == "NO_TRADE"]

        return {
            "total_predictions": len(entries),
            "resolved_trades": total,
            "pending_trades": len(entries) - total,
            "model_directional_accuracy": round(correct / total * 100, 1) if total > 0 else 0,
            "profitable_trades": profits,
            "losing_trades": losses,
            "breakeven_trades": breakeven,
            "hit_rate_pct": round(profits / total * 100, 1) if total > 0 else 0,
            "avg_pnl_pct": round(avg_pnl, 2),
            "total_pnl_pct": round(sum(pnls), 2),
            "user_confirmed_trades": len(confirmed_trades),
            "user_rejected_trades": len(rejected_trades),
            "gate_blocked_trades": len(no_trade_entries),
            "symbol_filter": symbol or "ALL",
            "timestamp": datetime.datetime.now().isoformat()
        }

    def get_rejected_trades_report(self) -> List[Dict[str, Any]]:
        """Get all rejected/blocked trades and their reasons."""
        data = self._read()
        entries = data.get("entries", [])

        rejected = []
        for e in entries:
            verdict = e.get("validation", {}).get("verdict", "")
            user_conf = e.get("user_confirmation", "")
            if verdict == "NO_TRADE" or user_conf == "REJECTED":
                reason = ""
                if verdict == "NO_TRADE":
                    gates = e.get("validation", {}).get("gates", {})
                    failed = [g for g, v in gates.items() if not v.get("passed", True)]
                    reason = f"Gates failed: {', '.join(failed)}" if failed else "Validation blocked"
                elif user_conf == "REJECTED":
                    reason = "User rejected the trade"

                rejected.append({
                    "id": e["id"],
                    "symbol": e["symbol"],
                    "signal": e["signal"],
                    "created_at": e["created_at"],
                    "reason": reason
                })

        return rejected
