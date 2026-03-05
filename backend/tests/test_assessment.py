"""Test stubs for assessment endpoint — Vinny implements these."""

import pytest

STUB = pytest.mark.skip(reason="stub — not yet implemented")


@STUB
class TestAssessmentEndpoint:
    def test_valid_assessment_returns_profile(self):
        raise NotImplementedError("Vinny implements this")

    def test_invalid_zip_rejected(self):
        raise NotImplementedError("Vinny implements this")

    def test_barrier_count_determines_severity(self):
        raise NotImplementedError("Vinny implements this")

    def test_credit_barrier_sets_needs_assessment(self):
        raise NotImplementedError("Vinny implements this")

    def test_no_vehicle_sets_transit_dependent(self):
        raise NotImplementedError("Vinny implements this")
