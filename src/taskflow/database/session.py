"""Database session configuration."""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from taskflow.database.engine import create_database_engine

engine = create_database_engine()

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_session() -> Generator[Session]:
    """Provide a database session and close it after use."""
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()