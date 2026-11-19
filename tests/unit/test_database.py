
"""Tests for database infrastructure."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from taskflow.core.config import settings
from taskflow.database.base import Base
from taskflow.database.engine import create_database_engine
from taskflow.database.session import get_session


def test_create_database_engine_uses_configured_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create an engine using the configured database settings."""
    monkeypatch.setattr(settings, "database_url", "sqlite:///:memory:")
    monkeypatch.setattr(settings, "database_echo", True)

    engine = create_database_engine()

    assert isinstance(engine, Engine)
    assert engine.url.database == ":memory:"
    assert engine.echo is True

    engine.dispose()


def test_base_has_metadata() -> None:
    """Expose SQLAlchemy metadata through the declarative base."""
    assert Base.metadata is not None
    assert set(Base.metadata.tables.keys()) == {"projects", "tasks"}


def test_get_session_closes_session_after_use(monkeypatch) -> None:
    """Close the database session after the generator finishes."""
    session = MagicMock(spec=Session)
    monkeypatch.setattr(
        "taskflow.database.session.SessionLocal",
        lambda: session,
    )

    session_generator = get_session()

    yielded_session = next(session_generator)

    assert yielded_session is session

    session_generator.close()

    session.close.assert_called_once()
