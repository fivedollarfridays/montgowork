"""Tests for database seed hardening and lifecycle functions."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core import database as db_module
from app.core.database import (
    ALLOWED_COLUMNS,
    _validate_seed_record,
    close_db,
    get_async_session_factory,
    get_db,
    get_engine,
    seed_database,
)


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


class TestGetEngine:
    def test_creates_engine_on_first_call(self):
        old = db_module._engine
        db_module._engine = None
        try:
            engine = get_engine()
            assert engine is not None
            assert db_module._engine is engine
        finally:
            db_module._engine = old

    def test_returns_cached_engine(self):
        old = db_module._engine
        sentinel = object()
        db_module._engine = sentinel
        try:
            assert get_engine() is sentinel
        finally:
            db_module._engine = old


class TestGetAsyncSessionFactory:
    def test_creates_factory_on_first_call(self):
        old_engine = db_module._engine
        old_factory = db_module._async_session_factory
        db_module._async_session_factory = None
        try:
            factory = get_async_session_factory()
            assert factory is not None
            assert db_module._async_session_factory is factory
        finally:
            db_module._engine = old_engine
            db_module._async_session_factory = old_factory

    def test_returns_cached_factory(self):
        old = db_module._async_session_factory
        sentinel = object()
        db_module._async_session_factory = sentinel
        try:
            assert get_async_session_factory() is sentinel
        finally:
            db_module._async_session_factory = old


class TestGetDb:
    @pytest.mark.anyio
    async def test_yields_session(self, test_engine):
        gen = get_db()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()


class TestCloseDb:
    @pytest.mark.anyio
    async def test_disposes_engine_and_resets_globals(self, tmp_path):
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'close_test.db'}", echo=False
        )
        old_engine = db_module._engine
        old_factory = db_module._async_session_factory
        db_module._engine = engine
        db_module._async_session_factory = "fake_factory"
        try:
            await close_db()
            assert db_module._engine is None
            assert db_module._async_session_factory is None
        finally:
            db_module._engine = old_engine
            db_module._async_session_factory = old_factory

    @pytest.mark.anyio
    async def test_noop_when_no_engine(self):
        old = db_module._engine
        db_module._engine = None
        try:
            await close_db()  # should not raise
            assert db_module._engine is None
        finally:
            db_module._engine = old


class TestSeedEdgeCases:
    @pytest.mark.anyio
    async def test_skips_when_already_seeded(self, test_engine):
        """seed_database should return early if resources already exist."""
        # init_db already seeds, so calling again should be a no-op
        async with test_engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM resources"))
            count_before = result.scalar()
        await seed_database(test_engine)
        async with test_engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM resources"))
            count_after = result.scalar()
        assert count_before == count_after

    @pytest.mark.anyio
    async def test_skips_missing_file(self, tmp_path):
        """seed_database should skip files that don't exist."""
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'missing.db'}", echo=False
        )
        from app.core.database import init_db
        # Point DATA_DIR to empty tmp_path so no seed files exist
        with patch.object(db_module, "DATA_DIR", tmp_path):
            async with engine.begin() as conn:
                for stmt in db_module.DDL_SQL.strip().split(";"):
                    stmt = stmt.strip()
                    if stmt:
                        await conn.execute(text(stmt))
            await seed_database(engine)
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT COUNT(*) FROM resources"))
                assert result.scalar() == 0
        await engine.dispose()

    @pytest.mark.anyio
    async def test_skips_empty_record(self, tmp_path):
        """seed_database should skip records that validate to empty dict."""
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'empty.db'}", echo=False
        )
        async with engine.begin() as conn:
            for stmt in db_module.DDL_SQL.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    await conn.execute(text(stmt))

        # Create a seed file with a record that has only disallowed columns
        seed_dir = tmp_path / "data"
        seed_dir.mkdir()
        (seed_dir / "career_centers.json").write_text(
            json.dumps([{"evil_col": "bad"}])
        )
        # Provide empty files for others so they're skipped
        for f in ["montgomery_businesses.json", "transit_routes.json",
                   "training_programs.json", "childcare_providers.json",
                   "community_resources.json"]:
            (seed_dir / f).write_text("[]")

        with patch.object(db_module, "DATA_DIR", seed_dir):
            await seed_database(engine)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM resources"))
            assert result.scalar() == 0
        await engine.dispose()
