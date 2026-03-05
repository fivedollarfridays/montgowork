from pydantic import BaseModel


class DocumentData(BaseModel):
    """Output from FixedPDF text extraction (Tier 3 -- optional)."""
    raw_text: str
    qualifications: list[str] = []
    certifications: list[dict] = []  # {type, issuer, expired: bool}
    work_history_entries: list[dict] = []  # {role, employer, duration}
