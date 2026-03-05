"""Matching engine core — takes a UserProfile and returns ranked resources."""

from app.modules.matching.types import UserProfile, ReEntryPlan, Resource, JobMatch, BarrierCard


async def generate_plan(profile: UserProfile, db_session) -> ReEntryPlan:
    """Orchestrate the full matching pipeline.

    1. Query resources matching the user's barriers
    2. Apply filters (credit, transit, childcare)
    3. Score and rank results
    4. Build barrier cards with action steps
    5. Return the complete ReEntryPlan
    """
    raise NotImplementedError("Kevin builds this")


async def query_resources_for_barriers(barriers: list, db_session) -> list[Resource]:
    """Query Montgomery data for resources matching the user's barrier types."""
    raise NotImplementedError("Kevin builds this")
