
"""Tests for domain model validation and updates."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from taskflow.domain.project import Project
from taskflow.domain.task import Task, TaskPriority


def test_project_rejects_empty_name() -> None:
    """Reject projects with an empty name."""
    with pytest.raises(ValueError, match="Project name cannot be empty"):
        Project(name="   ")


def test_project_strips_name_and_description() -> None:
    """Normalize project name and description."""
    project = Project(name="  TaskFlow  ", description="  Project description  ")

    assert project.name == "TaskFlow"
    assert project.description == "Project description"


def test_project_rejects_naive_creation_timestamp() -> None:
    """Reject a project creation timestamp without timezone information."""
    with pytest.raises(ValueError, match="creation timestamp must be timezone-aware"):
        Project(
            name="TaskFlow",
            created_at=datetime(2026, 1, 1),
        )


def test_project_update_details() -> None:
    """Update project details and timestamp."""
    project = Project(name="Original project")
    original_updated_at = project.updated_at

    project.update_details(
        name="  Updated project  ",
        description="  New description  ",
    )

    assert project.name == "Updated project"
    assert project.description == "New description"
    assert project.updated_at >= original_updated_at


def test_project_update_rejects_empty_name() -> None:
    """Reject an empty name during project updates."""
    project = Project(name="Original project")

    with pytest.raises(ValueError, match="Project name cannot be empty"):
        project.update_details(name="   ")


def test_task_rejects_empty_title() -> None:
    """Reject tasks with an empty title."""
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        Task(project_id=uuid4(), title="   ")


def test_task_strips_title_and_description() -> None:
    """Normalize task title and description."""
    task = Task(
        project_id=uuid4(),
        title="  Implement API  ",
        description="  API implementation  ",
    )

    assert task.title == "Implement API"
    assert task.description == "API implementation"


def test_task_rejects_naive_due_date() -> None:
    """Reject a due date without timezone information."""
    with pytest.raises(ValueError, match="due date must be timezone-aware"):
        Task(
            project_id=uuid4(),
            title="Implement API",
            due_date=datetime(2026, 12, 1),
        )


def test_task_update_details() -> None:
    """Update task details and timestamp."""
    task = Task(project_id=uuid4(), title="Original task")
    original_updated_at = task.updated_at
    due_date = datetime(2026, 12, 1, tzinfo=UTC)

    task.update_details(
        title="  Updated task  ",
        description="  Updated description  ",
        priority=TaskPriority.HIGH,
        due_date=due_date,
    )

    assert task.title == "Updated task"
    assert task.description == "Updated description"
    assert task.priority == TaskPriority.HIGH
    assert task.due_date == due_date
    assert task.updated_at >= original_updated_at


def test_task_update_rejects_empty_title() -> None:
    """Reject an empty title during task updates."""
    task = Task(project_id=uuid4(), title="Original task")

    with pytest.raises(ValueError, match="Task title cannot be empty"):
        task.update_details(title="   ")


def test_task_update_rejects_naive_due_date() -> None:
    """Reject a due date without timezone information during updates."""
    task = Task(project_id=uuid4(), title="Original task")

    with pytest.raises(ValueError, match="due date must be timezone-aware"):
        task.update_details(due_date=datetime(2026, 12, 1))


def test_task_update_priority() -> None:
    """Update task priority independently."""
    task = Task(project_id=uuid4(), title="Priority task")

    task.update_details(priority=TaskPriority.CRITICAL)

    assert task.priority == TaskPriority.CRITICAL


def test_task_update_description() -> None:
    """Update task description independently."""
    task = Task(project_id=uuid4(), title="Description task")

    task.update_details(description="  New description  ")

    assert task.description == "New description"
