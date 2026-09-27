import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class KronosRiskGate:
    """
    Hard Risk Gate for Kronos Agent Engine.
    Validates trade proposals against safety boundaries before execution.
    Acts as a circuit breaker for risky actions.
    """

    def __init__(self,
                 max_portfolio_exposure: float = 1.0,  # Max total exposure as % of total portfolio value
                 max_asset_exposure: float = 0.3,      # Max exposure per asset as % of total portfolio value
                 max_slippage_tolerance: float = 0.02, # Max tolerated slippage
                 min_risk_reward_ratio: float = 1.5,   # Minimum risk/reward ratio (take_profit distance / stop_loss distance)
                 max_stop_loss_pct: float = 0.10):     # Max tolerated stop loss distance (10%)
        self.max_portfolio_exposure = max_portfolio_exposure
        self.max_asset_exposure = max_asset_exposure
        self.max_slippage_tolerance = max_slippage_tolerance
        self.min_risk_reward_ratio = min_risk_reward_ratio
        self.max_stop_loss_pct = max_stop_loss_pct

    def validate_action(
        self,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        stop_loss: float,
        take_profit: float,
        portfolio_cash: float,
        portfolio_holdings: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates a trade proposal against hard risk rules.
        Returns a decision dictionary:
        {
            "approved": bool,
            "reason": str,
            "adjusted_quantity": float,
            "risk_metrics": dict
        }
        """
        action = action.upper()

        # 1. Parameter checking
        if price <= 0:
            return {
                "approved": False,
                "reason": f"Invalid price constraint: {price}",
                "adjusted_quantity": 0.0,
                "risk_metrics": {}
            }

        if quantity <= 0:
            return {
                "approved": False,
                "reason": f"Invalid quantity constraint: {quantity}",
                "adjusted_quantity": 0.0,
                "risk_metrics": {}
            }

        # Calculate current total portfolio value
        holdings_value = 0.0
        for s, hold in portfolio_holdings.items():
            holdings_value += hold.get("quantity", 0) * hold.get("current_price", price)

        total_portfolio_value = portfolio_cash + holdings_value
        if total_portfolio_value <= 0:
            # Fallback if empty portfolio
            total_portfolio_value = portfolio_cash if portfolio_cash > 0 else (price * quantity)

        proposed_value = price * quantity

        # 2. Sell Operations Validation
        if action == "SELL":
            current_qty = portfolio_holdings.get(symbol, {}).get("quantity", 0.0)
            if current_qty < quantity:
                return {
                    "approved": False,
                    "reason": f"Insufficient holdings footprint for {symbol}. Proposed sell: {quantity}, Owned: {current_qty}",
                    "adjusted_quantity": float(current_qty),
                    "risk_metrics": {
                        "proposed_value": proposed_value,
                        "owned_quantity": current_qty
                    }
                }

            # Simple Sell Approval
            return {
                "approved": True,
                "reason": "Validated sell proposal against available inventory.",
                "adjusted_quantity": float(quantity),
                "risk_metrics": {
                    "proposed_value": proposed_value,
                    "current_position_value": current_qty * price
                }
            }

        # 3. Buy Operations Validation
        if action == "BUY":
            # Cash availability check
            if proposed_value > portfolio_cash:
                adjusted_qty = portfolio_cash / price
                # Floor mapping or small buffer reduction (e.g. subtract a small slippage cushion)
                adjusted_qty = int(adjusted_qty) if adjusted_qty >= 1 else 0.0
                if adjusted_qty <= 0:
                    return {
                        "approved": False,
                        "reason": f"Insufficient buying power footprint. Proposed order cost: {proposed_value}, Cash: {portfolio_cash}",
                        "adjusted_quantity": 0.0,
                        "risk_metrics": {"portfolio_cash": portfolio_cash, "proposed_value": proposed_value}
                    }
                else:
                    quantity = float(adjusted_qty)
                    proposed_value = price * quantity
                    logger.info(f"Adjusted BUY quantity due to buying power constraints: {quantity}")

            # Stop Loss check
            if not stop_loss or stop_loss <= 0:
                # Default Stop Loss if missing
                stop_loss = price * (1.0 - 0.05)
            elif stop_loss >= price:
                return {
                    "approved": False,
                    "reason": f"Invalid stop loss coordinate for BUY. Entry price: {price}, Stop Loss: {stop_loss}",
                    "adjusted_quantity": 0.0,
                    "risk_metrics": {}
                }

            # Take Profit check
            if not take_profit or take_profit <= 0:
                # Default Take Profit if missing
                take_profit = price * (1.0 + 0.10)
            elif take_profit <= price:
                return {
                    "approved": False,
                    "reason": f"Invalid take profit coordinate for BUY. Entry price: {price}, Take Profit: {take_profit}",
                    "adjusted_quantity": 0.0,
                    "risk_metrics": {}
                }

            # Distance and risk/reward checking
            stop_dist = price - stop_loss
            tp_dist = take_profit - price
            stop_loss_pct = stop_dist / price

            if stop_loss_pct > self.max_stop_loss_pct:
                # Tighten stop loss or adjust position down
                target_stop = price * (1.0 - self.max_stop_loss_pct)
                return {
                    "approved": False,
                    "reason": f"Proposed stop loss distance too wide ({stop_loss_pct * 100:.2f}%). Limit is {self.max_stop_loss_pct * 100:.2f}%. Target SL: {target_stop}",
                    "adjusted_quantity": 0.0,
                    "risk_metrics": {
                        "stop_loss_pct": stop_loss_pct,
                        "max_stop_loss_pct": self.max_stop_loss_pct
                    }
                }

            # Risk-Reward check
            if stop_dist > 0:
                rr_ratio = tp_dist / stop_dist
                if rr_ratio < self.min_risk_reward_ratio:
                    return {
                        "approved": False,
                        "reason": f"Poor risk/reward profile. R:R ratio is {rr_ratio:.2fx} (Target min is {self.min_risk_reward_ratio:.2f}x).",
                        "adjusted_quantity": 0.0,
                        "risk_metrics": {
                            "risk_reward_ratio": rr_ratio,
                            "min_ratio": self.min_risk_reward_ratio
                        }
                    }

            # Asset Concentration check
            existing_asset_value = portfolio_holdings.get(symbol, {}).get("quantity", 0) * price
            new_asset_exposure = (existing_asset_value + proposed_value) / total_portfolio_value
            if new_asset_exposure > self.max_asset_exposure:
                # Re-scale quantity to meet concentration cap
                max_allowed_value = total_portfolio_value * self.max_asset_exposure
                allowed_proposed_value = max_allowed_value - existing_asset_value
                if allowed_proposed_value <= 0:
                    return {
                        "approved": False,
                        "reason": f"Asset concentration violation for {symbol}. Current exposure exceeds {self.max_asset_exposure * 100:.1f}%.",
                        "adjusted_quantity": 0.0,
                        "risk_metrics": {
                            "current_exposure_pct": (existing_asset_value / total_portfolio_value) * 100,
                            "cap_pct": self.max_asset_exposure * 100
                        }
                    }
                adjusted_qty = allowed_proposed_value / price
                # Safe floor scaling
                adjusted_qty = float(int(adjusted_qty))
                if adjusted_qty <= 0:
                    return {
                        "approved": False,
                        "reason": f"Concentration limit allows 0 quantity for {symbol}.",
                        "adjusted_quantity": 0.0,
                        "risk_metrics": {}
                    }
                quantity = adjusted_qty
                proposed_value = price * quantity
                logger.info(f"Adjusted BUY quantity due to asset concentration limits: {quantity}")

            # Total Portfolio Exposure check
            new_total_exposure = (holdings_value + proposed_value) / total_portfolio_value
            if new_total_exposure > self.max_portfolio_exposure:
                return {
                    "approved": False,
                    "reason": f"Total portfolio exposure ceiling exceeded: {new_total_exposure * 100:.1f}%. Limit: {self.max_portfolio_exposure * 100:.1f}%.",
                    "adjusted_quantity": 0.0,
                    "risk_metrics": {
                        "new_exposure_pct": new_total_exposure * 100,
                        "limit_pct": self.max_portfolio_exposure * 100
                    }
                }

            return {
                "approved": True,
                "reason": "Passed all hard gate validations.",
                "adjusted_quantity": float(quantity),
                "risk_metrics": {
                    "price": price,
                    "quantity": quantity,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "proposed_value": proposed_value,
                    "individual_exposure_pct": (proposed_value / total_portfolio_value) * 100,
                    "stop_loss_pct": (stop_dist / price) * 100
                }
            }

        return {
            "approved": False,
            "reason": f"Unknown trigger action direction: {action}",
            "adjusted_quantity": 0.0,
            "risk_metrics": {}
        }
