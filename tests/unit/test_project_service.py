
"""Tests for project service operations."""

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from taskflow.database.base import Base
from taskflow.domain.project import Project, ProjectStatus
from taskflow.models.project import ProjectModel
from taskflow.services.project_service import (
    ProjectNotFoundError,
    ProjectService,
)


def create_test_session() -> Session:
    """Create an isolated in-memory database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def create_project(name: str = "Test project") -> Project:
    """Create a domain project for testing."""
    return Project(
        name=name,
        description="Test description",
    )


def test_create_project() -> None:
    """Create and persist a project."""
    session = create_test_session()
    service = ProjectService(session)
    project = create_project()

    result = service.create(project)

    assert result.id == project.id
    assert result.name == project.name
    assert session.get(ProjectModel, project.id) is not None

    session.close()


def test_get_by_id_returns_project() -> None:
    """Return a project when it exists."""
    session = create_test_session()
    service = ProjectService(session)
    project = service.create(create_project())

    result = service.get_by_id(project.id)

    assert result is not None
    assert result.id == project.id

    session.close()


def test_get_by_id_returns_none_for_missing_project() -> None:
    """Return None when the project does not exist."""
    session = create_test_session()
    service = ProjectService(session)

    result = service.get_by_id(uuid4())

    assert result is None

    session.close()


def test_get_all_returns_projects() -> None:
    """Return all persisted projects."""
    session = create_test_session()
    service = ProjectService(session)

    first_project = service.create(create_project("First"))
    second_project = service.create(create_project("Second"))

    result = service.get_all()

    assert len(result) == 2
    assert {project.id for project in result} == {
        first_project.id,
        second_project.id,
    }

    session.close()


def test_update_details() -> None:
    """Update project name and description."""
    session = create_test_session()
    service = ProjectService(session)
    project = service.create(create_project())

    result = service.update_details(
        project.id,
        name="Updated project",
        description="Updated description",
    )

    assert result.name == "Updated project"
    assert result.description == "Updated description"

    session.close()


def test_update_details_raises_for_missing_project() -> None:
    """Raise an error when updating a missing project."""
    session = create_test_session()
    service = ProjectService(session)

    with pytest.raises(ProjectNotFoundError):
        service.update_details(uuid4(), name="Updated")

    session.close()


def test_change_status() -> None:
    """Change project status."""
    session = create_test_session()
    service = ProjectService(session)
    project = service.create(create_project())

    result = service.change_status(
        project.id,
        ProjectStatus.COMPLETED,
    )

    assert result.status == ProjectStatus.COMPLETED

    session.close()


def test_change_status_rejects_invalid_transition() -> None:
    """Reject an invalid project status transition."""
    session = create_test_session()
    service = ProjectService(session)
    project = service.create(create_project())

    service.change_status(project.id, ProjectStatus.ARCHIVED)

    with pytest.raises(ValueError):
        service.change_status(project.id, ProjectStatus.ACTIVE)

    session.close()


def test_change_status_raises_for_missing_project() -> None:
    """Raise an error when changing status of a missing project."""
    session = create_test_session()
    service = ProjectService(session)

    with pytest.raises(ProjectNotFoundError):
        service.change_status(uuid4(), ProjectStatus.COMPLETED)

    session.close()


def test_delete_project() -> None:
    """Delete an existing project."""
    session = create_test_session()
    service = ProjectService(session)
    project = service.create(create_project())

    service.delete(project.id)

    assert session.get(ProjectModel, project.id) is None

    session.close()


def test_delete_raises_for_missing_project() -> None:
    """Raise an error when deleting a missing project."""
    session = create_test_session()
    service = ProjectService(session)

    with pytest.raises(ProjectNotFoundError):
        service.delete(uuid4())

    session.close()


def test_create_rolls_back_on_failure() -> None:
    """Roll back the transaction when project creation fails."""
    session = create_test_session()
    ProjectService(session)

    class FailingService(ProjectService):
        """Simulate a database failure."""

        def _to_model(self, project: Project) -> ProjectModel:
            """Raise an error during model conversion."""
            raise RuntimeError("Simulated failure.")

    failing_service = FailingService(session)

    with pytest.raises(RuntimeError, match="Simulated failure"):
        failing_service.create(create_project())

    assert session.query(ProjectModel).count() == 0

    session.close()
