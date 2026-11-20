
"""Tests for project repository operations."""

from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from taskflow.database.base import Base
from taskflow.models.project import ProjectModel
from taskflow.repositories.project_repository import ProjectRepository


def create_test_session() -> Session:
    """Create an isolated in-memory database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def create_project(name: str = "Test project") -> ProjectModel:
    """Create a project model for testing."""
    return ProjectModel(
        id=uuid4(),
        name=name,
        description="Test description",
    )


def test_create_project() -> None:
    """Persist a project in the current transaction."""
    session = create_test_session()
    repository = ProjectRepository(session)
    project = create_project()

    result = repository.create(project)

    assert result.id == project.id
    assert session.get(ProjectModel, project.id) is not None

    session.close()


def test_get_by_id_returns_project() -> None:
    """Return a project when its ID exists."""
    session = create_test_session()
    project = create_project()
    session.add(project)
    session.flush()

    repository = ProjectRepository(session)

    result = repository.get_by_id(project.id)

    assert result is not None
    assert result.id == project.id

    session.close()


def test_get_by_id_returns_none_for_missing_project() -> None:
    """Return None when the project does not exist."""
    session = create_test_session()
    repository = ProjectRepository(session)

    result = repository.get_by_id(uuid4())

    assert result is None

    session.close()


def test_get_all_returns_projects_ordered_by_creation_date() -> None:
    """Return all projects ordered by creation date descending."""
    session = create_test_session()
    first_project = create_project("First")
    second_project = create_project("Second")

    session.add_all([first_project, second_project])
    session.flush()

    repository = ProjectRepository(session)

    result = repository.get_all()

    assert len(result) == 2
    assert result[0].created_at >= result[1].created_at

    session.close()


def test_update_project() -> None:
    """Persist changes to an existing project."""
    session = create_test_session()
    project = create_project()
    session.add(project)
    session.flush()

    repository = ProjectRepository(session)
    project.name = "Updated project"

    result = repository.update(project)

    assert result.name == "Updated project"
    assert session.get(ProjectModel, project.id).name == "Updated project"

    session.close()


def test_delete_project() -> None:
    """Delete a project from the current transaction."""
    session = create_test_session()
    project = create_project()
    session.add(project)
    session.flush()

    repository = ProjectRepository(session)

    repository.delete(project)

    assert session.get(ProjectModel, project.id) is None

    session.close()
