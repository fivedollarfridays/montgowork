"""Test stubs for matching engine filters — Vinny implements these."""

import pytest

STUB = pytest.mark.skip(reason="stub — not yet implemented")


@STUB
class TestCreditFilter:
    def test_high_severity_flags_background_check_jobs(self):
        raise NotImplementedError("Vinny implements this")

    def test_medium_severity_flags_finance_government(self):
        raise NotImplementedError("Vinny implements this")

    def test_low_severity_all_eligible(self):
        raise NotImplementedError("Vinny implements this")


@STUB
class TestTransitFilter:
    def test_filters_by_route_accessibility(self):
        raise NotImplementedError("Vinny implements this")

    def test_flags_sunday_jobs_no_transit(self):
        raise NotImplementedError("Vinny implements this")

    def test_flags_night_shift_no_transit(self):
        raise NotImplementedError("Vinny implements this")


@STUB
class TestChildcareFilter:
    def test_filters_by_proximity_to_home_and_work(self):
        raise NotImplementedError("Vinny implements this")


@STUB
class TestCertificationRenewal:
    def test_parses_cna_from_work_history(self):
        raise NotImplementedError("Vinny implements this")

    def test_parses_cdl_from_work_history(self):
        raise NotImplementedError("Vinny implements this")

    def test_returns_renewal_body_info(self):
        raise NotImplementedError("Vinny implements this")

    def test_matches_local_training_program(self):
        raise NotImplementedError("Vinny implements this")

    def test_generates_ordered_action_steps(self):
        raise NotImplementedError("Vinny implements this")
