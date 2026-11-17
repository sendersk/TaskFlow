
"""Tests for the task domain model."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from taskflow.domain.task import (
    Task,
    TaskPriority,
    TaskStatus,
)


def test_task_creation_uses_default_values() -> None:
    """Create a task with default values."""
    project_id = uuid4()
    task = Task(project_id=project_id, title="Implement API")

    assert task.project_id == project_id
    assert task.title == "Implement API"
    assert task.description == ""
    assert task.status == TaskStatus.TODO
    assert task.priority == TaskPriority.MEDIUM
    assert task.due_date is None
    assert isinstance(task.id, UUID)
    assert task.created_at.tzinfo == UTC
    assert task.updated_at.tzinfo == UTC


def test_task_creation_accepts_custom_values() -> None:
    """Create a task with custom values."""
    project_id = uuid4()
    due_date = datetime(2026, 12, 1, tzinfo=UTC)

    task = Task(
        project_id=project_id,
        title="Implement authentication",
        description="Add authentication endpoints",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        due_date=due_date,
    )

    assert task.project_id == project_id
    assert task.title == "Implement authentication"
    assert task.description == "Add authentication endpoints"
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.priority == TaskPriority.HIGH
    assert task.due_date == due_date


def test_tasks_receive_unique_ids() -> None:
    """Assign a unique identifier to each task."""
    project_id = uuid4()

    first_task = Task(project_id=project_id, title="Task A")
    second_task = Task(project_id=project_id, title="Task B")

    assert first_task.id != second_task.id


def test_task_default_status_is_todo() -> None:
    """Set TODO status for newly created tasks."""
    task = Task(project_id=uuid4(), title="New task")

    assert task.status == TaskStatus.TODO


def test_task_default_priority_is_medium() -> None:
    """Set MEDIUM priority for newly created tasks."""
    task = Task(project_id=uuid4(), title="New task")

    assert task.priority == TaskPriority.MEDIUM


def test_task_status_values() -> None:
    """Expose supported task status values."""
    assert TaskStatus.TODO.value == "todo"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.BLOCKED.value == "blocked"
    assert TaskStatus.COMPLETED.value == "completed"


def test_task_priority_values() -> None:
    """Expose supported task priority values."""
    assert TaskPriority.LOW.value == "low"
    assert TaskPriority.MEDIUM.value == "medium"
    assert TaskPriority.HIGH.value == "high"
    assert TaskPriority.CRITICAL.value == "critical"


def test_task_can_have_no_due_date() -> None:
    """Allow tasks without a due date."""
    task = Task(project_id=uuid4(), title="Unscheduled task")

    assert task.due_date is None
