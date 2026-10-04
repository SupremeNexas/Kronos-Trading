import datetime
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class MarketSnapshot(BaseModel):
    symbol: str
    provider: str
    timestamp: datetime.datetime
    interval: str
    current_price: float
    features: Dict[str, Any] = Field(default_factory=dict)
    data_quality: str = "GOOD" # or "INSUFFICIENT", "STALE"
    errors: List[str] = Field(default_factory=list)
    freshness_seconds: int = 0
    source_timestamp: Optional[datetime.datetime] = None

class ForecastDistribution(BaseModel):
    symbol: str
    forecast_model: str
    forecast_version: str
    timestamp: datetime.datetime
    current_price: float
    horizon: int
    expected_return_pct: float
    median_return_pct: float
    forecast_paths: Optional[List[List[float]]] = None
    lower_range: float
    upper_range: float
    uncertainty: float # sigma / dispersion
    confidence: float
    directional_prob: Optional[float] = None
    source_timestamp: datetime.datetime
    provider: str = "KRONOS"
    data_quality: str = "GOOD"
    missing_data_indicators: List[str] = Field(default_factory=list)

class InvestmentView(BaseModel):
    symbol: str
    forecast_reference: str # ID or timestamp
    view_return: float
    view_uncertainty: float
    confidence: float
    signal: str # "BUY", "SELL", "HOLD"
    supporting_evidence: str = ""
    opposing_evidence: str = ""
    decision_changing_conditions: str = ""

class PortfolioTarget(BaseModel):
    symbol: str
    target_weight: float
    current_weight: float
    weight_delta: float
    current_price: float
    risk_constraints: Dict[str, Any] = Field(default_factory=dict)

class RiskDecision(BaseModel):
    status: str # "ALLOW", "WARN", "BLOCK"
    decision: str
    reasons: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    blocking_conditions: List[str] = Field(default_factory=list)
    adjusted_quantity: float = 0.0

class ValidationState(BaseModel):
    status: str # "PASS", "WARN", "FAIL", "INSUFFICIENT_DATA"
    metrics: Dict[str, Any] = Field(default_factory=dict)
    reasons: List[str] = Field(default_factory=list)

class ExecutionPlan(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    symbol: str
    side: str
    quantity: float
    price_target: float
    order_type: str = "MARKET"
    time_in_force: str = "GTC"
    validation_status: str
    risk_status: str
    proposal_timestamp: datetime.datetime

class PaperOrderResult(BaseModel):
    order_id: str
    status: str
    filled_quantity: float
    filled_price: Optional[float]
    fees: float = 0.0
    error: Optional[str] = None
    broker: str = "ALPACA_PAPER"
    timestamp: datetime.datetime

class JournalEntry(BaseModel):
    run_id: str
    timestamp: datetime.datetime
    symbol: str
    market_data_source: str
    market_snapshot_ref: Dict[str, Any]
    forecast_model: str
    forecast_version: str
    forecast_distribution: Dict[str, Any]
    uncertainty: float
    investment_view: Dict[str, Any]
    portfolio_optimizer: str
    portfolio_optimizer_version: str
    target_weights: Dict[str, float]
    current_weights: Dict[str, float]
    turnover: float
    transaction_cost_assumption: float
    validation_metrics: Dict[str, Any]
    validation_gate_result: str
    risk_result: str
    confirmation_state: str
    order_id: Optional[str] = None
    paper_broker_result: Optional[Dict[str, Any]] = None
    review_notes: Optional[str] = None
