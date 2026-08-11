import os
import json
import datetime
import threading

class BrokerInterface:
    def get_balance(self) -> float:
        raise NotImplementedError
    def get_positions(self) -> dict:
        raise NotImplementedError
    def place_order(self, symbol: str, tx_type: str, qty: float, price: float) -> dict:
        raise NotImplementedError

class MockBroker(BrokerInterface):
    def __init__(self, portfolio_path: str = "webui/data/paper_portfolio.json"):
        self.portfolio_path = portfolio_path
        self.lock = threading.Lock()
        self._init_portfolio()

    def _init_portfolio(self):
        os.makedirs(os.path.dirname(self.portfolio_path), exist_ok=True)
        with self.lock:
            if not os.path.exists(self.portfolio_path):
                self._save_raw({"cash": 100000.0, "positions": {}, "history": []})

    def _read_data(self) -> dict:
        try:
            with open(self.portfolio_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"cash": 100000.0, "positions": {}, "history": []}

    def _save_raw(self, data: dict):
        temp_path = self.portfolio_path + ".tmp"
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, self.portfolio_path)

    def get_balance(self) -> float:
        with self.lock:
            return self._read_data().get("cash", 0.0)

    def get_positions(self) -> dict:
        with self.lock:
            return self._read_data().get("positions", {})

    def place_order(self, symbol: str, tx_type: str, qty: float, price: float) -> dict:
        tx_type = tx_type.upper()
        cost = qty * price

        with self.lock:
            data = self._read_data()
            cash = data["cash"]
            positions = data.get("positions", {})
            history = data.get("history", [])

            if tx_type == "BUY":
                if cash < cost:
                    return {"success": False, "error": "Insufficient cash balance"}
                data["cash"] -= cost
                pos = positions.get(symbol, {"quantity": 0.0, "entry_price": 0.0})
                total_qty = pos["quantity"] + qty
                # Calc weighted avg entry price
                weighted_price = ((pos["quantity"] * pos["entry_price"]) + cost) / total_qty
                positions[symbol] = {
                    "quantity": total_qty,
                    "entry_price": weighted_price,
                    "time": datetime.datetime.now().isoformat()
                }
            elif tx_type == "SELL":
                pos = positions.get(symbol, {"quantity": 0.0})
                if pos["quantity"] < qty:
                    return {"success": False, "error": f"Insufficient position quantity. Have {pos['quantity']}, want to sell {qty}"}
                data["cash"] += cost
                pos["quantity"] -= qty
                if pos["quantity"] <= 0:
                    positions.pop(symbol, None)
                else:
                    positions[symbol] = pos
            else:
                return {"success": False, "error": "Invalid transaction type"}

            history_entry = {
                "time": datetime.datetime.now().isoformat(),
                "symbol": symbol,
                "type": tx_type,
                "quantity": qty,
                "price": price
            }
            history.append(history_entry)

            data["positions"] = positions
            data["history"] = history
            self._save_raw(data)

            return {
                "success": True,
                "message": f"Successfully executed {tx_type} order for {qty} of {symbol}",
                "order": history_entry
            }
