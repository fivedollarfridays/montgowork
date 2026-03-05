from pydantic import BaseModel
from typing import Optional
from enum import Enum


class CrawlStatus(str, Enum):
    STARTING = "starting"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"


class CrawlRequest(BaseModel):
    urls: list[str]
    dataset_id: str
    output_fields: str = "markdown|ld_json|html2text"


class CrawlProgress(BaseModel):
    snapshot_id: str
    status: CrawlStatus
    progress_pct: Optional[float] = None


class CrawlResult(BaseModel):
    snapshot_id: str
    jobs: list[dict]  # Raw job data from Bright Data
