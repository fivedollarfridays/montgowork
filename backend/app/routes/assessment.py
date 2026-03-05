"""POST /api/assessment — Vinny implements this."""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from app.modules.matching.types import (
    AssessmentRequest,
    BarrierSeverity,
    BarrierType,
    UserProfile,
)

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


def determine_severity(barrier_count: int) -> BarrierSeverity:
    """3+ barriers = HIGH, 2 = MEDIUM, 1 = LOW."""
    raise NotImplementedError("Vinny implements this")


def extract_primary_barriers(barriers: dict[BarrierType, bool]) -> list[BarrierType]:
    """Return list of BarrierType enums for checked barriers."""
    raise NotImplementedError("Vinny implements this")


@router.post("/")
async def create_assessment(request: AssessmentRequest) -> dict:
    """Receive barrier form, create session, return profile summary.

    1. Validate zip_code is Montgomery area (361xx) — already enforced by Pydantic pattern
    2. Create session_id (UUID)
    3. Count barriers, determine severity
    4. Set flags: needs_credit_assessment, transit_dependent
    5. Store session in SQLite (expires in 24h)
    6. Return UserProfile
    """
    raise NotImplementedError("Vinny implements this")
