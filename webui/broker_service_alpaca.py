import os
import uuid
import datetime
from typing import Dict, Any, List, Optional
import logging

try:
    from posthog import Posthog
    POSTHOG_API_KEY = os.environ.get("POSTHOG_API_KEY", "")
    POSTHOG_HOST = os.environ.get("POSTHOG_HOST", "https://app.posthog.com")
    posthog = Posthog(POSTHOG_API_KEY, host=POSTHOG_HOST) if POSTHOG_API_KEY else None
except ImportError:
    posthog = None

def track_event(event_name, properties=None):
    if posthog:
        try:
            safe_props = properties.copy() if properties else {}
            for k in list(safe_props.keys()):
                if 'key' in k.lower() or 'token' in k.lower() or 'password' in k.lower(): safe_props[k] = "***"
            posthog.capture('anonymous_user', event_name, safe_props)
        except Exception:
            pass


try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

from webui.broker_service import RiskEngine, MockBrokerAdapter

class AlpacaBrokerAdapter:
    def __init__(self):
        self.risk_engine = RiskEngine()
        api_key = os.environ.get("ALPACA_API_KEY", "") or os.environ.get("APCA_API_KEY_ID", "")
        secret_key = os.environ.get("ALPACA_SECRET_KEY", "") or os.environ.get("APCA_API_SECRET_KEY", "")
        
        # Enforce PAPER ONLY
        is_paper = os.environ.get("ALPACA_PAPER_TRADE", "true").lower() == "true"
        if not is_paper:
            logging.critical("LIVE TRADING DETECTED. Fail safe activated. KRONOS MUST remain PAPER ONLY.")
            raise Exception("FAIL SAFE: Live trading is not allowed. Check ALPACA_PAPER_TRADE.")
            
        if ALPACA_AVAILABLE and api_key and secret_key:
            self.client = TradingClient(api_key, secret_key, paper=True)
            self.available = True
        else:
            self.client = None
            self.available = False
            logging.warning("Alpaca not configured. Operations will fail gracefully.")

    def get_trading_mode(self) -> Dict[str, Any]:
        return {
            "mode": "paper",
            "kill_switch_active": self.risk_engine.kill_switch_active,
            "broker_name": "Alpaca Paper Trading",
            "is_paper": True,
            "max_order_value": self.risk_engine.max_order_value,
            "max_position_value": self.risk_engine.max_position_value,
            "max_daily_loss": self.risk_engine.max_daily_loss
        }

    def set_kill_switch(self, active: bool) -> Dict[str, Any]:
        self.risk_engine.kill_switch_active = active
        return {
            "success": True,
            "kill_switch_active": active,
            "message": f"Trading kill switch has been {'ACTIVATED' if active else 'DEACTIVATED'}."
        }

    def get_balance(self) -> float:
        if not self.available: return 0.0
        try:
            acct = self.client.get_account()
            return float(acct.cash)
        except Exception:
            return 0.0

    def get_positions_dict(self) -> Dict[str, Any]:
        if not self.available: return {}
        try:
            positions = self.client.get_all_positions()
            pos_dict = {}
            for p in positions:
                pos_dict[p.symbol] = {
                    "quantity": float(p.qty),
                    "entry_price": float(p.avg_entry_price)
                }
            return pos_dict
        except Exception:
            return {}

    def get_account(self, mark_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if not self.available:
            return {"error": "Alpaca not configured", "cash": 0}
        
        try:
            acct = self.client.get_account()
            return {
                "portfolio_value": float(acct.portfolio_value),
                "cash": float(acct.cash),
                "buying_power": float(acct.buying_power),
                "positions_value": float(acct.equity) - float(acct.cash),
                "day_pnl": float(acct.portfolio_value) - float(acct.last_equity),
                "total_pnl": float(acct.portfolio_value) - 100000.0, # Approximate if initial cash unknown
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
                "trading_mode": "PAPER",
                "broker_name": "Alpaca Paper Trading",
                "kill_switch_active": self.risk_engine.kill_switch_active
            }
        except Exception as e:
            logging.error(f"Alpaca get_account error: {e}")
            return {"error": str(e), "cash": 0}

    def get_positions(self, mark_prices: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        if not self.available: return []
        try:
            positions = self.client.get_all_positions()
            res = []
            for p in positions:
                res.append({
                    "symbol": p.symbol,
                    "quantity": float(p.qty),
                    "average_price": float(p.avg_entry_price),
                    "current_price": float(p.current_price),
                    "market_value": float(p.market_value),
                    "day_pnl": float(p.unrealized_intraday_pl),
                    "total_pnl": float(p.unrealized_pl),
                    "pnl_pct": float(p.unrealized_plpc) * 100,
                    "opened_at": ""
                })
            return res
        except Exception as e:
            logging.error(f"Alpaca get_positions error: {e}")
            return []

    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.available: return []
        try:
            from alpaca.trading.requests import GetOrdersRequest
            from alpaca.trading.enums import QueryOrderStatus
            req_status = QueryOrderStatus.ALL
            if status:
                if status.upper() == "OPEN": req_status = QueryOrderStatus.OPEN
                elif status.upper() == "CLOSED": req_status = QueryOrderStatus.CLOSED
            req = GetOrdersRequest(status=req_status)
            orders = self.client.get_orders(req)
            
            res = []
            for o in orders:
                res.append({
                    "order_id": str(o.id),
                    "time": o.created_at.isoformat() if o.created_at else "",
                    "symbol": o.symbol,
                    "side": o.side.value if hasattr(o.side, 'value') else str(o.side),
                    "quantity": float(o.qty) if o.qty else 0.0,
                    "order_type": o.order_type.value if hasattr(o.order_type, 'value') else str(o.order_type),
                    "price": float(o.limit_price) if o.limit_price else 0.0,
                    "status": o.status.value if hasattr(o.status, 'value') else str(o.status),
                    "filled_quantity": float(o.filled_qty) if o.filled_qty else 0.0,
                    "idempotency_key": str(o.client_order_id)
                })
            return res
        except Exception as e:
            logging.error(f"Alpaca get_orders error: {e}")
            return []

    def get_executions(self) -> List[Dict[str, Any]]:
        # Map alpaca filled orders to executions for simplicity
        orders = self.get_orders(status="CLOSED")
        return [o for o in orders if o["status"] == "filled" or o["filled_quantity"] > 0]

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
        if not self.available:
            return {"success": False, "error": "Alpaca client not configured"}

        # Format symbol for Alpaca (e.g. AAPL.US -> AAPL)
        alpaca_sym = symbol.replace(".US", "").split(".")[0]

        # Risk check
        try:
            account = self.client.get_account()
            cash = float(account.cash)
            positions = self.client.get_all_positions()
            
            cur_pos_qty = 0.0
            cur_pos_val = 0.0
            for p in positions:
                if p.symbol == alpaca_sym:
                    cur_pos_qty = float(p.qty)
                    cur_pos_val = float(p.market_value)
                    
            risk_check = self.risk_engine.validate_order(
                symbol=alpaca_sym,
                side=side,
                quantity=quantity,
                price=price if price > 0 else 1.0, # mock price if market
                account_balance=cash,
                current_position_qty=cur_pos_qty,
                current_position_val=cur_pos_val
            )
            
            if not risk_check["valid"]:
                track_event('risk_check_failed', {'symbol': alpaca_sym, 'side': side, 'reason': risk_check["reason"]})
                return {"success": False, "error": risk_check["reason"]}
            track_event('risk_check_passed', {'symbol': alpaca_sym, 'side': side})
                
            # Submit to alpaca
            side_enum = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            tif_enum = TimeInForce.DAY if time_in_force.upper() == "DAY" else TimeInForce.GTC
            
            client_oid = idempotency_key or f"kronos-{uuid.uuid4().hex[:8]}"
            
            if order_type.upper() == "MARKET":
                req = MarketOrderRequest(
                    symbol=alpaca_sym,
                    qty=quantity,
                    side=side_enum,
                    time_in_force=tif_enum,
                    client_order_id=client_oid
                )
                order = self.client.submit_order(order_data=req)
            else:
                req = LimitOrderRequest(
                    symbol=alpaca_sym,
                    qty=quantity,
                    side=side_enum,
                    time_in_force=tif_enum,
                    limit_price=price,
                    client_order_id=client_oid
                )
                order = self.client.submit_order(order_data=req)
                
            return {
                "success": True,
                "message": f"Successfully submitted {side} order to Alpaca.",
                "order": {
                    "order_id": str(order.id),
                    "idempotency_key": str(order.client_order_id)
                }
            }

        except Exception as e:
            logging.error(f"Alpaca place_order error: {e}")
            return {"success": False, "error": f"Alpaca error: {e}"}

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        if not self.available: return {"success": False, "error": "Alpaca client not configured"}
        try:
            self.client.cancel_order_by_id(order_id)
            return {"success": True, "message": f"Order {order_id} cancelled."}
        except Exception as e:
            return {"success": False, "error": str(e)}

