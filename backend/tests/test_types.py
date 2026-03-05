"""Coverage tests for type-only modules and logging."""

from app.ai.types import AnalysisResult, PlanNarrative
from app.core.logging import get_logger
from app.integrations.brightdata.types import (
    CrawlProgress,
    CrawlRequest,
    CrawlResult,
    CrawlStatus,
)
from app.modules.data.types import Employer, TransitRoute, TransitStop, WorkforceResource
from app.modules.documents.types import DocumentData


class TestAITypes:
    def test_analysis_result(self):
        r = AnalysisResult(
            extracted_qualifications=["CNA"],
            certification_status=[{"type": "CNA", "status": "expired"}],
            barrier_interpretation="Credit barrier is primary.",
        )
        assert r.extracted_qualifications == ["CNA"]

    def test_plan_narrative(self):
        n = PlanNarrative(summary="Go to bus stop.", key_actions=["Call WIOA"])
        assert n.summary == "Go to bus stop."


class TestBrightDataTypes:
    def test_crawl_status_values(self):
        assert CrawlStatus.READY == "ready"
        assert CrawlStatus.FAILED == "failed"

    def test_crawl_request(self):
        r = CrawlRequest(urls=["https://example.com"], dataset_id="abc")
        assert r.output_fields == "markdown|ld_json|html2text"

    def test_crawl_progress(self):
        p = CrawlProgress(snapshot_id="s1", status=CrawlStatus.RUNNING)
        assert p.progress_pct is None

    def test_crawl_result(self):
        r = CrawlResult(snapshot_id="s1", jobs=[{"title": "Clerk"}])
        assert len(r.jobs) == 1


class TestDataTypes:
    def test_employer(self):
        e = Employer(id=1, name="ACME")
        assert e.active is True

    def test_transit_route(self):
        r = TransitRoute(id=1, route_number=7, route_name="East Side")
        assert r.sunday is False

    def test_transit_stop(self):
        s = TransitStop(id=1, route_id=1, stop_name="Main St", lat=32.3, lng=-86.2)
        assert s.sequence is None

    def test_workforce_resource(self):
        w = WorkforceResource(id=1, name="WIOA Center", category="career_center")
        assert w.services is None


class TestDocumentTypes:
    def test_document_data_defaults(self):
        d = DocumentData(raw_text="Some text")
        assert d.qualifications == []
        assert d.certifications == []
        assert d.work_history_entries == []


class TestLogging:
    def test_get_logger_returns_logger(self):
        log = get_logger("test_module")
        assert log is not None
