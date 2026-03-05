"""Resource relevance scoring."""

from app.modules.matching.types import UserProfile, Resource


def score_resource(resource: Resource, profile: UserProfile) -> float:
    """Score a resource's relevance to a specific user profile.

    Factors: barrier match, proximity (if transit-dependent),
    industry match, schedule compatibility.
    Returns: 0.0 - 1.0
    """
    raise NotImplementedError("Kevin builds this")


def rank_resources(resources: list[Resource], profile: UserProfile) -> list[Resource]:
    """Rank resources by relevance score, descending."""
    raise NotImplementedError("Kevin builds this")
