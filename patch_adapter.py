import re

with open('webui/broker_service_alpaca.py', 'r') as f:
    text = f.read()

account_method = '''    def get_account(self, mark_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if not self.available:
            return {"error": "Alpaca not configured", "cash": 0}

        try:
            acct = self.client.get_account()

            pv = float(acct.portfolio_value)
            le = float(acct.last_equity)
            dp = float(pv) - float(le)
            dp_pct = (dp / le * 100) if le > 0 else 0.0

            # Approximate total pnl if init cash unknown. We'll use 100,000 as default paper cash.
            init_cash = 100000.0
            tp = pv - init_cash
            tp_pct = (tp / init_cash * 100)

            return {
                "total_equity": pv,
                "portfolio_value": pv,
                "cash": float(acct.cash),
                "buying_power": float(acct.buying_power),
                "positions_value": float(acct.equity) - float(acct.cash),
                "day_pnl": dp,
                "today_pnl": dp,
                "today_pnl_pct": dp_pct,
                "total_pnl": tp,
                "unrealized_pnl": tp,
                "unrealized_pnl_pct": tp_pct,
                "realized_pnl": 0.0,
                "trading_mode": "PAPER",
                "broker_name": "Alpaca Paper Trading",
                "kill_switch_active": self.risk_engine.kill_switch_active
            }
        except Exception as e:
            logging.error(f"Alpaca get_account error: {e}")
            return {"error": str(e), "cash": 0}'''

text = re.sub(r'    def get_account\(self, mark_prices.*?return \{"error": str\(e\), "cash": 0\}', account_method, text, flags=re.DOTALL)

positions_method = '''    def get_positions(self, mark_prices: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        if not self.available: return []
        try:
            positions = self.client.get_all_positions()
            res = []
            for p in positions:
                res.append({
                    "symbol": p.symbol,
                    "side": p.side.value if hasattr(p.side, 'value') else str(p.side.name if hasattr(p.side, 'name') else p.side),
                    "quantity": float(p.qty),
                    "avg_price": float(p.avg_entry_price),
                    "average_price": float(p.avg_entry_price),
                    "current_price": float(p.current_price),
                    "market_value": float(p.market_value),
                    "day_pnl": float(p.unrealized_intraday_pl),
                    "total_pnl": float(p.unrealized_pl),
                    "unrealized_pnl": float(p.unrealized_pl),
                    "unrealized_pnl_pct": float(p.unrealized_plpc) * 100,
                    "pnl_pct": float(p.unrealized_plpc) * 100,
                    "opened_at": ""
                })
            return res
        except Exception as e:
            logging.error(f"Alpaca get_positions error: {e}")
            return []'''

text = re.sub(r'    def get_positions\(self, mark_prices.*?return \[\]', positions_method, text, flags=re.DOTALL)

with open('webui/broker_service_alpaca.py', 'w') as f:
    f.write(text)
