
"""Tests for task service operations."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from taskflow.database.base import Base
from taskflow.domain.project import Project
from taskflow.domain.task import Task, TaskPriority, TaskStatus
from taskflow.models.project import ProjectModel
from taskflow.models.task import TaskModel
from taskflow.services.task_service import TaskNotFoundError, TaskService


def create_test_session() -> Session:
    """Create an isolated in-memory database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def create_project(session: Session) -> ProjectModel:
    """Create and persist a project for task tests."""
    project = Project(name="Test project")
    model = ProjectModel(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )
    session.add(model)
    session.commit()
    return model


def create_task(project_id: object, **overrides: object) -> Task:
    """Create a domain task for testing."""
    values: dict[str, object] = {
        "project_id": project_id,
        "title": "Test task",
        "description": "Test description",
    }
    values.update(overrides)
    return Task(**values)  # type: ignore[arg-type]


def create_persisted_task(
    session: Session,
    service: TaskService,
    project_id: object,
) -> Task:
    """Create and persist a task."""
    task = create_task(project_id)
    return service.create(task)


def test_create_task() -> None:
    """Create and persist a task."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)

    task = create_task(project.id)
    result = service.create(task)

    assert result.id == task.id
    assert result.project_id == project.id
    assert result.title == "Test task"
    assert session.get(TaskModel, task.id) is not None

    session.close()


def test_get_by_id_returns_task() -> None:
    """Return a task when it exists."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)
    task = create_persisted_task(session, service, project.id)

    result = service.get_by_id(task.id)

    assert result is not None
    assert result.id == task.id

    session.close()


def test_get_by_id_returns_none_for_missing_task() -> None:
    """Return None when the task does not exist."""
    session = create_test_session()
    service = TaskService(session)

    assert service.get_by_id(uuid4()) is None

    session.close()


def test_get_by_project_id_returns_tasks() -> None:
    """Return all tasks belonging to a project."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)

    first = create_persisted_task(session, service, project.id)
    second = create_persisted_task(session, service, project.id)

    result = service.get_by_project_id(project.id)

    assert {task.id for task in result} == {first.id, second.id}

    session.close()


def test_list_by_project_filters_and_paginates() -> None:
    """Apply status, priority, and pagination filters."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)

    first = service.create(
        create_task(
            project.id,
            title="First",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
        )
    )
    second = service.create(
        create_task(
            project.id,
            title="Second",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
        )
    )
    service.create(
        create_task(
            project.id,
            title="Third",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
        )
    )

    filtered = service.list_by_project(
        project.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
    )
    assert [task.id for task in filtered] == [first.id]

    paginated = service.list_by_project(project.id, limit=1, offset=1)
    assert len(paginated) == 1
    assert paginated[0].id == second.id

    session.close()


def test_update_details() -> None:
    """Update task title, description, priority, and due date."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)
    task = create_persisted_task(session, service, project.id)
    due_date = datetime.now(UTC) + timedelta(days=3)

    result = service.update_details(
        task.id,
        title="Updated task",
        description="Updated description",
        priority=TaskPriority.CRITICAL,
        due_date=due_date,
    )

    assert result.title == "Updated task"
    assert result.description == "Updated description"
    assert result.priority == TaskPriority.CRITICAL
    assert result.due_date == due_date

    session.close()


def test_update_details_raises_for_missing_task() -> None:
    """Raise an error when updating a missing task."""
    session = create_test_session()
    service = TaskService(session)

    with pytest.raises(TaskNotFoundError):
        service.update_details(uuid4(), title="Updated")

    session.close()


def test_update_details_rejects_empty_title() -> None:
    """Reject an empty task title."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)
    task = create_persisted_task(session, service, project.id)

    with pytest.raises(ValueError, match="Task title cannot be empty"):
        service.update_details(task.id, title=" ")

    session.close()


def test_change_status() -> None:
    """Change task status."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)
    task = create_persisted_task(session, service, project.id)

    result = service.change_status(task.id, TaskStatus.IN_PROGRESS)

    assert result.status == TaskStatus.IN_PROGRESS

    session.close()


def test_change_status_rejects_invalid_transition() -> None:
    """Reject an invalid task status transition."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)
    task = create_persisted_task(session, service, project.id)

    with pytest.raises(ValueError, match="Cannot change task status"):
        service.change_status(task.id, TaskStatus.COMPLETED)

    session.close()


def test_change_status_raises_for_missing_task() -> None:
    """Raise an error when changing status of a missing task."""
    session = create_test_session()
    service = TaskService(session)

    with pytest.raises(TaskNotFoundError):
        service.change_status(uuid4(), TaskStatus.IN_PROGRESS)

    session.close()


def test_delete_task() -> None:
    """Delete an existing task."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)
    task = create_persisted_task(session, service, project.id)

    service.delete(task.id)

    assert session.get(TaskModel, task.id) is None

    session.close()


def test_delete_raises_for_missing_task() -> None:
    """Raise an error when deleting a missing task."""
    session = create_test_session()
    service = TaskService(session)

    with pytest.raises(TaskNotFoundError):
        service.delete(uuid4())

    session.close()


def test_create_preserves_timezone_information() -> None:
    """Restore UTC timezone information for SQLite timestamps."""
    session = create_test_session()
    project = create_project(session)
    service = TaskService(session)
    due_date = datetime.now(UTC) + timedelta(days=1)

    task = service.create(create_task(project.id, due_date=due_date))

    assert task.created_at.tzinfo is not None
    assert task.updated_at.tzinfo is not None
    assert task.due_date is not None
    assert task.due_date.tzinfo is not None

    session.close()
