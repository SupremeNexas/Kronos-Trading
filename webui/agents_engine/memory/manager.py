import os
import json
import datetime
import logging
from webui.agents_engine.config import RESULTS_DIR

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, memory_path: str = None):
        if memory_path is None:
            self.memory_path = os.path.join(RESULTS_DIR, "agent_memory.json")
        else:
            self.memory_path = memory_path
        self._init_memory()

    def _init_memory(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, 'w') as f:
                json.dump({"entries": []}, f, indent=2)

    def _read_memory(self) -> dict:
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {"entries": []}

    def _write_memory(self, data: dict):
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write agent memory file: {e}")

    def store_decision(self, symbol: str, ai_decision: dict, kronos_direction: str, risk_level: str, entry_price: float):
        """Append a new trading decision to memory log."""
        data = self._read_memory()

        entry = {
            "symbol": symbol,
            "analysis_date": datetime.datetime.now().isoformat(),
            "ai_decision": ai_decision, # Dict containing action, confidence, etc.
            "entry_price": entry_price,
            "kronos_direction": kronos_direction,
            "risk_level": risk_level,
            "resolved": False,
            "eventual_outcome": None,
            "performance_return_pct": 0.0,
            "lessons": ""
        }

        data["entries"].append(entry)
        # Limit memory history to avoid massive file growth, keep last 200 items max
        if len(data["entries"]) > 200:
             data["entries"] = data["entries"][-200:]

        self._write_memory(data)

    def resolve_outcomes(self, symbol: str, current_price: float):
        """
        Evaluate previous unresolved decision entries of an asset.
        Performs post-trade reflections and updates lessons.
        """
        data = self._read_memory()
        updated = False

        for entry in data.get("entries", []):
            if entry["symbol"] == symbol and not entry.get("resolved", False):
                # We trace if the trade reached exit limits
                prev_price = entry["entry_price"]
                action = entry["ai_decision"].get("action", "HOLD").upper()

                # Check direction correctness
                ret_pct = 0.0
                if prev_price > 0.0:
                    ret_pct = ((current_price - prev_price) / prev_price) * 100.0

                if action == "BUY":
                    outcome = "PROFIT" if ret_pct > 0.0 else "LOSS"
                    perf = ret_pct
                elif action == "SELL":
                    outcome = "PROFIT" if ret_pct < 0.0 else "LOSS"
                    perf = -ret_pct
                else:
                    outcome = "NEUTRAL"
                    perf = 0.0

                # Formulate reflections
                lessons = []
                # Match direction with Kronos prediction
                k_dir = entry["kronos_direction"].upper()
                if (k_dir == "BULLISH" and ret_pct > 0.0) or (k_dir == "BEARISH" and ret_pct < 0.0):
                    lessons.append("Kronos model numerical forecast direction was correct.")
                else:
                    lessons.append("Kronos model numerical forecast got directional bias wrong.")

                if outcome == "PROFIT":
                    lessons.append("Technical/Fundamental triggers was positive and generated gain.")
                else:
                    lessons.append("Analysis failed to capture downside volatility catalysts.")

                entry["resolved"] = True
                entry["eventual_outcome"] = outcome
                entry["performance_return_pct"] = float(round(perf, 2))
                entry["lessons"] = " ".join(lessons)
                updated = True

        if updated:
            self._write_memory(data)

    def get_past_reflections(self, symbol: str, limit: int = 3) -> list:
        """Fetch past reflections of an asset to pass to LLMs as history."""
        data = self._read_memory()
        history = []
        for entry in reversed(data.get("entries", [])):
            if entry["symbol"] == symbol and entry.get("resolved", False):
                history.append({
                    "date": entry["analysis_date"],
                    "decision": entry["ai_decision"].get("action"),
                    "outcome": entry["eventual_outcome"],
                    "return_pct": entry["performance_return_pct"],
                    "lessons": entry["lessons"]
                })
                if len(history) >= limit:
                    break
        return history
