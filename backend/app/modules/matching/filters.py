"""Matching engine filters — Vinny implements these."""

from app.modules.matching.types import UserProfile, Resource, JobMatch


def apply_credit_filter(
    jobs: list[JobMatch], credit_severity: str,
) -> tuple[list[JobMatch], list[JobMatch]]:
    """Split jobs into eligible_now vs eligible_after_repair based on credit barrier.

    Args:
        jobs: All matched jobs
        credit_severity: "high", "medium", or "low" from credit API

    Returns:
        (eligible_now, eligible_after_repair)

    Rules:
        - HIGH severity: flag all jobs that typically require background checks
        - MEDIUM: flag only finance/government jobs
        - LOW: all jobs eligible now
    """
    raise NotImplementedError("Vinny implements this")


def apply_transit_filter(
    jobs: list[JobMatch], routes: list, user_zip: str,
) -> list[JobMatch]:
    """Filter jobs by M Transit accessibility.

    Args:
        jobs: All matched jobs
        routes: Transit routes from DB
        user_zip: Resident's zip code

    Returns:
        Jobs with transit_accessible and route fields populated.
        Jobs requiring Sunday/night work flagged as
        "requires personal transportation"
        (M Transit has NO Sunday service, weekday service ends ~9pm)
    """
    raise NotImplementedError("Vinny implements this")


def apply_childcare_filter(
    resources: list[Resource], user_zip: str, employer_zips: list[str],
) -> list[Resource]:
    """Filter childcare providers by proximity to both home and work.

    Returns providers near the user's zip AND near matched employer locations.
    """
    raise NotImplementedError("Vinny implements this")


def get_certification_renewal(
    work_history: str, certifications: list[dict] | None = None,
) -> list[dict]:
    """Identify expired/expiring certifications and generate renewal pathways.

    Flow:
        1. Parse work_history text for certification keywords (CNA, CDL, etc.)
        2. Look up renewal body (e.g. Alabama Board of Nursing for CNA)
        3. Match to local training programs (e.g. MRWTC for healthcare certs)
        4. Estimate timeline (CNA reinstatement = 6-8 weeks typical)
        5. Generate ordered action steps

    Returns:
        List of dicts, each containing:
        {
            "certification_type": "CNA",
            "status": "expired",
            "renewal_body": {"name": "Alabama Board of Nursing",
                             "phone": "334-242-4060"},
            "training_program": {"name": "MRWTC",
                                 "program": "Healthcare Re-Certification"},
            "estimated_days": 45,
            "steps": ["Call Alabama Board of Nursing...",
                      "Contact MRWTC...", ...]
        }

    Data source: training_programs in SQLite (already seeded).
    """
    raise NotImplementedError("Vinny implements this")
