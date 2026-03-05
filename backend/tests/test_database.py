"""Tests for database seed hardening."""

import pytest

from app.core.database import ALLOWED_COLUMNS, _validate_seed_record


class TestSeedValidation:
    def test_valid_table_passes(self):
        """Known table name should not raise."""
        _validate_seed_record("resources", {"name": "Test", "category": "test"})

    def test_unknown_table_raises(self):
        """Unknown table name should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown seed table"):
            _validate_seed_record("malicious_table", {"name": "Test"})

    def test_disallowed_column_filtered(self):
        """Columns not in ALLOWED_COLUMNS should be stripped."""
        clean = _validate_seed_record(
            "resources",
            {"name": "Test", "category": "test", "evil_col": "drop table"},
        )
        assert "evil_col" not in clean
        assert "name" in clean

    def test_all_allowed_columns_preserved(self):
        """All allowed columns should pass through."""
        record = {"name": "Test", "category": "test", "phone": "555-1234"}
        clean = _validate_seed_record("resources", record)
        assert clean == record

    def test_json_fields_serialized(self):
        """List/dict values in JSON_FIELDS should be serialized to strings."""
        record = {"name": "Test", "category": "test", "services": ["a", "b"]}
        clean = _validate_seed_record("resources", record)
        assert clean["services"] == '["a", "b"]'
