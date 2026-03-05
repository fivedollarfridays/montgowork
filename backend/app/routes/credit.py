"""POST /api/credit/assess — Thin proxy to credit assessment API."""

import httpx
from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.modules.credit.types import (
    CreditAssessmentResult,
    CreditProfileRequest,
    score_to_band,
)

router = APIRouter(prefix="/api/credit", tags=["credit"])


@router.post("/assess")
async def assess_credit(profile: CreditProfileRequest) -> CreditAssessmentResult:
    """Proxy to the credit assessment microservice.

    Auto-derives score_band from current_score to prevent 422s.
    Returns typed CreditAssessmentResult.
    """
    settings = get_settings()
    payload = profile.model_dump()
    payload["score_band"] = score_to_band(profile.current_score)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.credit_api_url}/v1/assess",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": settings.credit_api_key,
                },
            )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Credit assessment service unavailable. Ensure it's running on the configured port.",
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=resp.json().get("detail", "Credit API error"),
        )
    return resp.json()
