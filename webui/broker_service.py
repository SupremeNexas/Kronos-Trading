import os
import json
import uuid
import datetime
import threading
from typing import Dict, Any, List, Optional

PORTFOLIO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'paper_portfolio.json')
AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'audit_log.json')
os.makedirs(os.path.dirname(PORTFOLIO_PATH), exist_ok=True)

class RiskEngine:
    """
    Server-side Risk Controls & Order Safety Validation Engine.
    Configurable limits:
      - TRADING_MODE (paper / live)
      - MAX_ORDER_VALUE (default 50,000 USD)
      - MAX_POSITION_VALUE (default 100,000 USD)
      - MAX_DAILY_LOSS (default 5,000 USD)
      - DISABLE_LIVE_TRADING / Kill switch flag
    """

    def __init__(self):
        self.trading_mode = os.environ.get("TRADING_MODE", "paper").lower()
        self.max_order_value = float(os.environ.get("MAX_ORDER_VALUE", "50000"))
        self.max_position_value = float(os.environ.get("MAX_POSITION_VALUE", "100000"))
        self.max_daily_loss = float(os.environ.get("MAX_DAILY_LOSS", "5000"))
        self.kill_switch_active = False

    def validate_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        account_balance: float,
        current_position_qty: float = 0.0,
        current_position_val: float = 0.0
    ) -> Dict[str, Any]:
        """Server-side order validation"""
        if self.kill_switch_active:
            return {"valid": False, "reason": "KILL SWITCH ACTIVE: Live and paper trading are temporarily disabled by administrator safety override."}

        if not symbol or not isinstance(symbol, str):
            return {"valid": False, "reason": "Invalid or missing order symbol."}

        side_upper = side.upper()
        if side_upper not in ["BUY", "SELL"]:
            return {"valid": False, "reason": f"Invalid order side: '{side}'. Must be 'BUY' or 'SELL'."}

        if quantity <= 0:
            return {"valid": False, "reason": f"Invalid quantity: {quantity}. Quantity must be positive."}

        if price <= 0:
            return {"valid": False, "reason": f"Invalid price: ${price}. Order price must be positive."}

        order_value = quantity * price

        # Check maximum order value limit
        if order_value > self.max_order_value:
            return {
                "valid": False,
                "reason": f"Order value (${order_value:,.2f}) exceeds configured MAX_ORDER_VALUE limit of ${self.max_order_value:,.2f}."
            }

        # Check BUY side constraints
        if side_upper == "BUY":
            if account_balance < order_value:
                return {
                    "valid": False,
                    "reason": f"Insufficient buying power. Required: ${order_value:,.2f}, Available: ${account_balance:,.2f}."
                }

            new_position_value = current_position_val + order_value
            if new_position_value > self.max_position_value:
                return {
                    "valid": False,
                    "reason": f"Resulting position value (${new_position_value:,.2f}) would exceed MAX_POSITION_VALUE limit of ${self.max_position_value:,.2f}."
                }

        # Check SELL side constraints
        if side_upper == "SELL":
            if current_position_qty < quantity:
                return {
                    "valid": False,
                    "reason": f"Insufficient position quantity. Available to sell: {current_position_qty}, Requested: {quantity}."
                }

        return {"valid": True, "reason": "Order passed server-side safety checks."}

class MockBrokerAdapter:
    """
    Broker-Agnostic Mock / Paper Broker Adapter implementation.
    Manages portfolio cash, positions, order ticket submissions, idempotency, order statuses, and executions.
    Default mode: PAPER TRADING.
    """

    def __init__(self, portfolio_path: str = PORTFOLIO_PATH):
        self.portfolio_path = portfolio_path
        self.lock = threading.Lock()
        self.risk_engine = RiskEngine()
        self.processed_idempotency_keys = set()
        self._init_portfolio()

    def _init_portfolio(self):
        with self.lock:
            if not os.path.exists(self.portfolio_path):
                initial_data = {
                    "cash": 100000.0,
                    "initial_cash": 100000.0,
                    "positions": {},
                    "orders": [],
                    "executions": [],
                    "realized_pnl": 0.0,
                    "mode": "paper",
                    "broker_name": "Paper Broker"
                }
                self._save_raw(initial_data)
            else:
                data = self._read_data()
                for o in data.get("orders", []):
                    if "idempotency_key" in o and o["idempotency_key"]:
                        self.processed_idempotency_keys.add(o["idempotency_key"])

    def _read_data(self) -> dict:
        default_data = {
            "cash": 100000.0,
            "initial_cash": 100000.0,
            "positions": {},
            "orders": [],
            "executions": [],
            "realized_pnl": 0.0,
            "mode": "paper",
            "broker_name": "Paper Broker"
        }
        try:
            if not os.path.exists(self.portfolio_path):
                return default_data
            with open(self.portfolio_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    return default_data
                return json.loads(content)
        except Exception:
            return default_data

    def _save_raw(self, data: dict):
        temp_path = self.portfolio_path + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, self.portfolio_path)

    def _log_audit(self, action: str, details: Dict[str, Any]):
        """Record audit log entry for sensitive broker operations"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        try:
            logs = []
            if os.path.exists(AUDIT_LOG_PATH):
                with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            logs.append(entry)
            with open(AUDIT_LOG_PATH, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Audit log writing error: {e}")

    def get_trading_mode(self) -> Dict[str, Any]:
        with self.lock:
            data = self._read_data()
            return {
                "mode": self.risk_engine.trading_mode,
                "kill_switch_active": self.risk_engine.kill_switch_active,
                "broker_name": data.get("broker_name", "Paper Broker"),
                "is_paper": self.risk_engine.trading_mode == "paper",
                "max_order_value": self.risk_engine.max_order_value,
                "max_position_value": self.risk_engine.max_position_value,
                "max_daily_loss": self.risk_engine.max_daily_loss
            }

    def set_kill_switch(self, active: bool) -> Dict[str, Any]:
        self.risk_engine.kill_switch_active = active
        self._log_audit("TOGGLE_KILL_SWITCH", {"active": active})
        return {
            "success": True,
            "kill_switch_active": active,
            "message": f"Trading kill switch has been {'ACTIVATED' if active else 'DEACTIVATED'}."
        }

    def get_balance(self) -> float:
        with self.lock:
            return self._read_data().get("cash", 100000.0)

    def get_positions_dict(self) -> Dict[str, Any]:
        with self.lock:
            return self._read_data().get("positions", {})

    def get_account(self, mark_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculates comprehensive account metrics including P&L and buying power"""
        with self.lock:
            data = self._read_data()
            cash = data.get("cash", 100000.0)
            initial_cash = data.get("initial_cash", 100000.0)
            realized_pnl = data.get("realized_pnl", 0.0)
            positions = data.get("positions", {})

            mark_prices = mark_prices or {}
            unrealized_pnl = 0.0
            positions_market_val = 0.0

            for sym, pos in positions.items():
                qty = pos.get("quantity", 0.0)
                entry_px = pos.get("entry_price", 0.0)
                current_px = mark_prices.get(sym, entry_px)
                market_val = qty * current_px
                pos_unrealized = (current_px - entry_px) * qty
                unrealized_pnl += pos_unrealized
                positions_market_val += market_val

            portfolio_value = round(cash + positions_market_val, 2)
            total_pnl = round(realized_pnl + unrealized_pnl, 2)
            total_pnl_pct = round((total_pnl / (initial_cash or 1.0)) * 100, 2)

            return {
                "portfolio_value": portfolio_value,
                "cash": round(cash, 2),
                "buying_power": round(cash, 2),
                "positions_value": round(positions_market_val, 2),
                "day_pnl": round(unrealized_pnl * 0.15, 2),  # Simulated day move component
                "total_pnl": total_pnl,
                "total_pnl_pct": total_pnl_pct,
                "unrealized_pnl": round(unrealized_pnl, 2),
                "realized_pnl": round(realized_pnl, 2),
                "trading_mode": self.risk_engine.trading_mode.upper(),
                "broker_name": data.get("broker_name", "Paper Broker"),
                "kill_switch_active": self.risk_engine.kill_switch_active
            }

    def get_positions(self, mark_prices: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Returns structured list of positions with current prices and P&L metrics"""
        with self.lock:
            data = self._read_data()
            positions_raw = data.get("positions", {})
            mark_prices = mark_prices or {}

            pos_list = []
            for sym, pos in positions_raw.items():
                qty = float(pos.get("quantity", 0.0))
                if qty <= 0:
                    continue
                entry_price = float(pos.get("entry_price", 0.0))
                current_price = float(mark_prices.get(sym, entry_price))
                market_value = round(qty * current_price, 2)
                unrealized_pnl = round((current_price - entry_price) * qty, 2)
                pnl_pct = round(((current_price - entry_price) / (entry_price or 1.0)) * 100, 2)

                pos_list.append({
                    "symbol": sym,
                    "quantity": qty,
                    "average_price": round(entry_price, 2),
                    "current_price": round(current_price, 2),
                    "market_value": market_value,
                    "day_pnl": round(unrealized_pnl * 0.2, 2),
                    "total_pnl": unrealized_pnl,
                    "pnl_pct": pnl_pct,
                    "opened_at": pos.get("time", "")
                })

            return pos_list

    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.lock:
            data = self._read_data()
            orders = data.get("orders", [])
            if status:
                orders = [o for o in orders if o.get("status", "").upper() == status.upper()]
            return sorted(orders, key=lambda x: x.get("time", ""), reverse=True)

    def get_executions(self) -> List[Dict[str, Any]]:
        with self.lock:
            data = self._read_data()
            executions = data.get("executions", [])
            return sorted(executions, key=lambda x: x.get("time", ""), reverse=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "Market",
        price: float = 0.0,
        trigger_price: float = 0.0,
        time_in_force: str = "DAY",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits and validates order ticket with safety rules, idempotency protection, and fill processing.
        """
        symbol = symbol.upper()
        side = side.upper()
        order_type = order_type.title()  # Market, Limit, Stop, Stop-Limit
        idempotency_key = idempotency_key or f"ik_{uuid.uuid4().hex[:12]}"

        with self.lock:
            # Check duplicate submission / idempotency key
            if idempotency_key in self.processed_idempotency_keys:
                return {
                    "success": False,
                    "error": "DUPLICATE_ORDER: An order with this idempotency key was already submitted."
                }

            data = self._read_data()
            cash = data.get("cash", 100000.0)
            positions = data.get("positions", {})
            orders = data.get("orders", [])
            executions = data.get("executions", [])
            realized_pnl = data.get("realized_pnl", 0.0)

            cur_pos_qty = positions.get(symbol, {}).get("quantity", 0.0)
            cur_pos_val = cur_pos_qty * price

            # Risk engine server-side validation
            risk_check = self.risk_engine.validate_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                account_balance=cash,
                current_position_qty=cur_pos_qty,
                current_position_val=cur_pos_val
            )

            if not risk_check["valid"]:
                # Log rejected order
                rejected_order = {
                    "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
                    "time": datetime.datetime.now().isoformat(),
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "order_type": order_type,
                    "price": price,
                    "trigger_price": trigger_price,
                    "time_in_force": time_in_force,
                    "status": "Rejected",
                    "rejection_reason": risk_check["reason"],
                    "filled_quantity": 0.0,
                    "idempotency_key": idempotency_key
                }
                orders.append(rejected_order)
                data["orders"] = orders
                self._save_raw(data)
                self._log_audit("ORDER_REJECTED", rejected_order)
                return {"success": False, "error": risk_check["reason"], "order": rejected_order}

            self.processed_idempotency_keys.add(idempotency_key)
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            now_iso = datetime.datetime.now().isoformat()

            # Execute order (Market orders fill immediately, Limit/Stop fill immediately at current price for paper trading)
            total_cost = quantity * price
            fill_price = price

            if side == "BUY":
                data["cash"] -= total_cost
                pos = positions.get(symbol, {"quantity": 0.0, "entry_price": 0.0})
                old_qty = pos.get("quantity", 0.0)
                old_entry = pos.get("entry_price", 0.0)
                new_qty = old_qty + quantity
                new_entry = ((old_qty * old_entry) + total_cost) / (new_qty or 1.0)

                positions[symbol] = {
                    "quantity": new_qty,
                    "entry_price": round(new_entry, 2),
                    "time": now_iso
                }
            elif side == "SELL":
                pos = positions.get(symbol, {"quantity": 0.0, "entry_price": 0.0})
                old_entry = pos.get("entry_price", price)
                pos_realized = (price - old_entry) * quantity
                realized_pnl += pos_realized

                data["cash"] += total_cost
                new_qty = pos["quantity"] - quantity
                if new_qty <= 0:
                    positions.pop(symbol, None)
                else:
                    pos["quantity"] = new_qty
                    positions[symbol] = pos

            order_record = {
                "order_id": order_id,
                "time": now_iso,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "order_type": order_type,
                "price": price,
                "trigger_price": trigger_price,
                "time_in_force": time_in_force,
                "status": "Filled",
                "filled_quantity": quantity,
                "avg_fill_price": fill_price,
                "idempotency_key": idempotency_key
            }

            execution_record = {
                "execution_id": f"EXEC-{uuid.uuid4().hex[:8].upper()}",
                "order_id": order_id,
                "time": now_iso,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": fill_price,
                "value": round(total_cost, 2)
            }

            orders.append(order_record)
            executions.append(execution_record)

            data["positions"] = positions
            data["orders"] = orders
            data["executions"] = executions
            data["realized_pnl"] = round(realized_pnl, 2)

            self._save_raw(data)
            self._log_audit("ORDER_EXECUTED", order_record)

            return {
                "success": True,
                "message": f"Successfully executed {side} order for {quantity} {symbol} @ ${fill_price:,.2f}",
                "order": order_record,
                "execution": execution_record
            }

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        with self.lock:
            data = self._read_data()
            orders = data.get("orders", [])
            for o in orders:
                if o.get("order_id") == order_id:
                    if o.get("status") in ["Open", "Pending"]:
                        o["status"] = "Cancelled"
                        data["orders"] = orders
                        self._save_raw(data)
                        self._log_audit("ORDER_CANCELLED", {"order_id": order_id})
                        return {"success": True, "message": f"Order {order_id} cancelled."}
                    return {"success": False, "error": f"Cannot cancel order in status '{o.get('status')}'"}
            return {"success": False, "error": f"Order {order_id} not found."}
