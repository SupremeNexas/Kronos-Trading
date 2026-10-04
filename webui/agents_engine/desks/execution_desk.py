import datetime
import logging
from typing import Optional
from webui.agents_engine.desk_schemas import PortfolioTarget, RiskDecision, ExecutionPlan, PaperOrderResult
import uuid

logger = logging.getLogger(__name__)

class ExecutionDesk:
    """
    Translates PortfolioTarget and RiskDecision into ExecutionPlan.
    Mocking full NautilusTrader abstraction for synchronous usage, keeping API consistent.
    """
    def __init__(self, broker_client=None):
        self.broker_client = broker_client

    def create_plan(self, target: PortfolioTarget, risk: RiskDecision, validation_status: str) -> ExecutionPlan:
        side = "BUY" if target.weight_delta > 0 else "SELL"
        if target.weight_delta == 0:
            side = "HOLD"

        return ExecutionPlan(
            symbol=target.symbol,
            side=side,
            quantity=risk.adjusted_quantity if risk.status != "BLOCK" else 0.0,
            price_target=target.current_price,
            validation_status=validation_status,
            risk_status=risk.status,
            proposal_timestamp=datetime.datetime.now()
        )

    def execute_paper(self, plan: ExecutionPlan, force_confirm: bool = False) -> PaperOrderResult:
        if plan.risk_status == "BLOCK" or plan.validation_status in ["FAIL", "INSUFFICIENT_DATA"]:
            return PaperOrderResult(
                order_id="REJECTED",
                status="REJECTED",
                filled_quantity=0.0,
                filled_price=None,
                error="Blocked by Risk/Validation",
                timestamp=datetime.datetime.now()
            )

        if not force_confirm:
            return PaperOrderResult(
                order_id="PENDING",
                status="PENDING_CONFIRMATION",
                filled_quantity=0.0,
                filled_price=None,
                error="Waiting for manual confirmation",
                timestamp=datetime.datetime.now()
            )

        # Actual execution logic (to Alpaca paper via broker_client)
        try:
            if self.broker_client and plan.quantity > 0:
                logger.info(f"Submitting to Alpaca PAPER: {plan.side} {plan.quantity} {plan.symbol}")
                # Mock response for now, assume success
                order_id = f"alpaca_paper_{uuid.uuid4().hex[:8]}"
                return PaperOrderResult(
                    order_id=order_id,
                    status="FILLED",
                    filled_quantity=plan.quantity,
                    filled_price=plan.price_target,
                    timestamp=datetime.datetime.now()
                )
            else:
                return PaperOrderResult(
                    order_id="NO_TRADE",
                    status="IGNORED",
                    filled_quantity=0.0,
                    filled_price=None,
                    timestamp=datetime.datetime.now()
                )
        except Exception as e:
            logger.error(f"Execution Error: {e}")
            return PaperOrderResult(
                order_id="FAILED",
                status="FAILED",
                filled_quantity=0.0,
                filled_price=None,
                error=str(e),
                timestamp=datetime.datetime.now()
            )
