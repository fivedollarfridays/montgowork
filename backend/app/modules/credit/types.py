from pydantic import BaseModel, Field
from typing import Optional


class AccountSummary(BaseModel):
    """Credit API account summary -- required fields only."""
    total_accounts: int = Field(..., ge=0)
    open_accounts: int = Field(..., ge=0)
    closed_accounts: int = Field(0, ge=0)
    negative_accounts: int = Field(0, ge=0)
    collection_accounts: int = Field(0, ge=0)
    total_balance: float = Field(0.0, ge=0)
    total_credit_limit: float = Field(0.0, ge=0)
    monthly_payments: float = Field(0.0, ge=0)


class CreditProfileRequest(BaseModel):
    """Maps to the credit assessment API's CreditProfile input."""
    current_score: int = Field(..., ge=300, le=850)
    score_band: Optional[str] = None  # Auto-derived by proxy if missing
    overall_utilization: float = Field(..., ge=0.0, le=100.0)
    account_summary: AccountSummary
    payment_history_pct: float = Field(..., ge=0.0, le=100.0)
    average_account_age_months: int = Field(..., ge=0, le=1200)
    negative_items: list[str] = Field(default_factory=list, max_length=50)


class CreditAssessmentResult(BaseModel):
    """Matches the actual /v1/assess response shape from the credit API.
    Uses dicts for nested structures -- the credit API owns these contracts."""
    barrier_severity: str
    barrier_details: list[dict]
    readiness: dict       # {score, fico_score, score_band, factors: {payment_history, utilization, ...}}
    thresholds: list[dict] # [{threshold_name, threshold_score, estimated_days, already_met, confidence}]
    dispute_pathway: dict  # {steps: [{step_number, action, description, ...}], total_estimated_days, statutes_cited}
    eligibility: list[dict] # [{product_name, category, required_score, status, gap_points, estimated_days_to_eligible}]
    disclaimer: str


def score_to_band(score: int) -> str:
    """Auto-derive score band from FICO score. Prevents 422 from the credit API."""
    if score >= 750: return "excellent"
    if score >= 700: return "good"
    if score >= 650: return "fair"
    if score >= 600: return "poor"
    return "very_poor"
