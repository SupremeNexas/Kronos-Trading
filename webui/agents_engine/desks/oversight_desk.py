import logging
from typing import Dict, Any, List
from webui.agents_engine.desk_schemas import ForecastDistribution, ValidationState, RiskDecision, InvestmentView

logger = logging.getLogger(__name__)

class OversightDesk:
    """
    LLM Oversight Layer. Only acts as research assistant / analyst overlay.
    Must NOT submit orders or change validation states.
    """
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def review_cycle(self, forecast: ForecastDistribution, view: InvestmentView, validation: ValidationState, risk: RiskDecision) -> Dict[str, Any]:
        # Here we would call the LLM for a structured research report.
        # We enforce read-only and no overrides.
        return {
            "research_conclusion": view.signal,
            "supporting_evidence": view.supporting_evidence,
            "opposing_evidence": view.opposing_evidence,
            "missing_information": "Real-time news feed omitted",
            "decision_changing_conditions": "A sudden market crash or FED reversal could invalidate this",
            "risk_concerns": risk.reasons,
            "validation_summary": validation.status
        }
