
"""Tests for project and task status transitions."""

from uuid import uuid4

import pytest

from taskflow.domain.project import Project, ProjectStatus
from taskflow.domain.task import Task, TaskStatus

# Project status transitions


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        (ProjectStatus.ACTIVE, ProjectStatus.COMPLETED),
        (ProjectStatus.ACTIVE, ProjectStatus.ARCHIVED),
        (ProjectStatus.COMPLETED, ProjectStatus.ACTIVE),
        (ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED),
    ],
)
def test_project_allows_valid_status_transitions(
    current_status: ProjectStatus,
    new_status: ProjectStatus,
) -> None:
    """Allow valid project status transitions."""
    project = Project(name="TaskFlow", status=current_status)

    project.change_status(new_status)

    assert project.status == new_status


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        (ProjectStatus.ACTIVE, ProjectStatus.ACTIVE),
        (ProjectStatus.COMPLETED, ProjectStatus.COMPLETED),
        (ProjectStatus.ARCHIVED, ProjectStatus.ACTIVE),
        (ProjectStatus.ARCHIVED, ProjectStatus.COMPLETED),
        (ProjectStatus.ARCHIVED, ProjectStatus.ARCHIVED),
    ],
)
def test_project_rejects_invalid_status_transitions(
    current_status: ProjectStatus,
    new_status: ProjectStatus,
) -> None:
    """Reject invalid project status transitions."""
    project = Project(name="TaskFlow", status=current_status)

    with pytest.raises(ValueError, match="Cannot change project status"):
        project.change_status(new_status)


# Task status transitions


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.TODO, TaskStatus.BLOCKED),
        (TaskStatus.IN_PROGRESS, TaskStatus.TODO),
        (TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED),
        (TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED),
        (TaskStatus.BLOCKED, TaskStatus.TODO),
        (TaskStatus.BLOCKED, TaskStatus.IN_PROGRESS),
        (TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS),
    ],
)
def test_task_allows_valid_status_transitions(
    current_status: TaskStatus,
    new_status: TaskStatus,
) -> None:
    """Allow valid task status transitions."""
    task = Task(project_id=uuid4(), title="Implement API", status=current_status)

    task.change_status(new_status)

    assert task.status == new_status


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        (TaskStatus.TODO, TaskStatus.TODO),
        (TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS),
        (TaskStatus.BLOCKED, TaskStatus.BLOCKED),
        (TaskStatus.BLOCKED, TaskStatus.COMPLETED),
        (TaskStatus.COMPLETED, TaskStatus.COMPLETED),
        (TaskStatus.COMPLETED, TaskStatus.TODO),
        (TaskStatus.COMPLETED, TaskStatus.BLOCKED),
    ],
)
def test_task_rejects_invalid_status_transitions(
    current_status: TaskStatus,
    new_status: TaskStatus,
) -> None:
    """Reject invalid task status transitions."""
    task = Task(project_id=uuid4(), title="Implement API", status=current_status)

    with pytest.raises(ValueError, match="Cannot change task status"):
        task.change_status(new_status)


def test_project_status_transition_updates_timestamp() -> None:
    """Update the project timestamp after a status transition."""
    project = Project(name="TaskFlow")
    original_updated_at = project.updated_at

    project.change_status(ProjectStatus.COMPLETED)

    assert project.updated_at >= original_updated_at


def test_task_status_transition_updates_timestamp() -> None:
    """Update the task timestamp after a status transition."""
    task = Task(project_id=uuid4(), title="Implement API")
    original_updated_at = task.updated_at

    task.change_status(TaskStatus.IN_PROGRESS)

    assert task.updated_at >= original_updated_at
