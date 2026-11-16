
"""Tests for the project domain model."""

from datetime import UTC
from uuid import UUID

from taskflow.domain.project import Project, ProjectStatus


def test_project_creation_uses_default_values() -> None:
    """Create a project with default values."""
    project = Project(name="TaskFlow")

    assert project.name == "TaskFlow"
    assert project.description == ""
    assert project.status == ProjectStatus.ACTIVE
    assert isinstance(project.id, UUID)
    assert project.created_at.tzinfo == UTC
    assert project.updated_at.tzinfo == UTC


def test_project_creation_accepts_custom_values() -> None:
    """Create a project with custom values."""
    project = Project(
        name="Backend API",
        description="Develop a REST API",
        status=ProjectStatus.COMPLETED,
    )

    assert project.name == "Backend API"
    assert project.description == "Develop a REST API"
    assert project.status == ProjectStatus.COMPLETED


def test_projects_receive_unique_ids() -> None:
    """Assign a unique identifier to each project."""
    first_project = Project(name="Project A")
    second_project = Project(name="Project B")

    assert first_project.id != second_project.id


def test_project_default_status_is_active() -> None:
    """Set active status for newly created projects."""
    project = Project(name="New project")

    assert project.status == ProjectStatus.ACTIVE


def test_project_status_values() -> None:
    """Expose supported project status values."""
    assert ProjectStatus.ACTIVE.value == "active"
    assert ProjectStatus.COMPLETED.value == "completed"
    assert ProjectStatus.ARCHIVED.value == "archived"
