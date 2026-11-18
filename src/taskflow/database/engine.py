"""Database engine configuration."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from taskflow.core.config import settings


def create_database_engine() -> Engine:
    """Create and configure the SQLAlchemy database engine."""
    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        future=True,
    )