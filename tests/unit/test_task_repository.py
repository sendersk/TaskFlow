
"""Tests for task repository operations."""

from uuid import UUID, uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from taskflow.database.base import Base
from taskflow.domain.task import TaskPriority, TaskStatus
from taskflow.models.project import ProjectModel
from taskflow.models.task import TaskModel
from taskflow.repositories.task_repository import TaskRepository


def create_test_session() -> Session:
    """Create an isolated in-memory database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def create_project() -> ProjectModel:
    """Create a project model for testing."""
    return ProjectModel(
        id=uuid4(),
        name="Test project",
        description="Test description",
    )


def create_task(project_id: UUID) -> TaskModel:
    """Create a task model for testing."""
    return TaskModel(
        id=uuid4(),
        project_id=project_id,
        title="Test task",
        description="Test description",
    )


def test_create_task() -> None:
    """Persist a task in the current transaction."""
    session = create_test_session()
    project = create_project()
    session.add(project)
    session.flush()

    repository = TaskRepository(session)
    task = create_task(project.id)

    result = repository.create(task)

    assert result.id == task.id
    assert session.get(TaskModel, task.id) is not None

    session.close()


def test_get_by_id_returns_task() -> None:
    """Return a task when its ID exists."""
    session = create_test_session()
    project = create_project()
    task = create_task(project.id)
    session.add_all([project, task])
    session.flush()

    repository = TaskRepository(session)

    result = repository.get_by_id(task.id)

    assert result is not None
    assert result.id == task.id

    session.close()


def test_get_by_id_returns_none_for_missing_task() -> None:
    """Return None when the task does not exist."""
    session = create_test_session()
    repository = TaskRepository(session)

    result = repository.get_by_id(uuid4())

    assert result is None

    session.close()


def test_get_by_project_id_returns_project_tasks() -> None:
    """Return only tasks belonging to the requested project."""
    session = create_test_session()
    project = create_project()
    other_project = create_project()
    first_task = create_task(project.id)
    second_task = create_task(project.id)
    other_task = create_task(other_project.id)

    session.add_all(
        [project, other_project, first_task, second_task, other_task]
    )
    session.flush()

    repository = TaskRepository(session)

    result = repository.get_by_project_id(project.id)

    assert len(result) == 2
    assert {task.id for task in result} == {
        first_task.id,
        second_task.id,
    }

    session.close()


def test_update_task() -> None:
    """Persist changes to an existing task."""
    session = create_test_session()
    project = create_project()
    task = create_task(project.id)
    session.add_all([project, task])
    session.flush()

    repository = TaskRepository(session)
    task.title = "Updated task"

    result = repository.update(task)

    assert result.title == "Updated task"
    persisted_task = session.get(TaskModel, task.id)
    assert persisted_task is not None
    assert persisted_task.title == "Updated task"

    session.close()


def test_delete_task() -> None:
    """Delete a task from the current transaction."""
    session = create_test_session()
    project = create_project()
    task = create_task(project.id)
    session.add_all([project, task])
    session.flush()

    repository = TaskRepository(session)

    repository.delete(task)

    assert session.get(TaskModel, task.id) is None

    session.close()



def test_list_by_project_filters_by_status() -> None:
    """Return only tasks matching the requested status."""
    session = create_test_session()
    project = create_project()

    todo_task = create_task(project.id)
    in_progress_task = create_task(project.id)
    in_progress_task.status = TaskStatus.IN_PROGRESS

    session.add_all([project, todo_task, in_progress_task])
    session.flush()

    repository = TaskRepository(session)

    result = repository.list_by_project(
        project_id=project.id,
        status=TaskStatus.IN_PROGRESS,
    )

    assert len(result) == 1
    assert result[0].id == in_progress_task.id

    session.close()


def test_list_by_project_filters_by_priority() -> None:
    """Return only tasks matching the requested priority."""
    session = create_test_session()
    project = create_project()

    low_priority_task = create_task(project.id)
    high_priority_task = create_task(project.id)
    high_priority_task.priority = TaskPriority.HIGH

    session.add_all([project, low_priority_task, high_priority_task])
    session.flush()

    repository = TaskRepository(session)

    result = repository.list_by_project(
        project_id=project.id,
        priority=TaskPriority.HIGH,
    )

    assert len(result) == 1
    assert result[0].id == high_priority_task.id

    session.close()


def test_list_by_project_filters_by_status_and_priority() -> None:
    """Apply status and priority filters together."""
    session = create_test_session()
    project = create_project()

    matching_task = create_task(project.id)
    matching_task.status = TaskStatus.IN_PROGRESS
    matching_task.priority = TaskPriority.HIGH

    wrong_status_task = create_task(project.id)
    wrong_status_task.priority = TaskPriority.HIGH

    wrong_priority_task = create_task(project.id)
    wrong_priority_task.status = TaskStatus.IN_PROGRESS

    session.add_all(
        [project, matching_task, wrong_status_task, wrong_priority_task]
    )
    session.flush()

    repository = TaskRepository(session)

    result = repository.list_by_project(
        project_id=project.id,
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
    )

    assert len(result) == 1
    assert result[0].id == matching_task.id

    session.close()


def test_list_by_project_applies_limit() -> None:
    """Return no more than the requested number of tasks."""
    session = create_test_session()
    project = create_project()

    tasks = [create_task(project.id) for _ in range(3)]
    session.add_all([project, *tasks])
    session.flush()

    repository = TaskRepository(session)

    result = repository.list_by_project(
        project_id=project.id,
        limit=2,
    )

    assert len(result) == 2

    session.close()


def test_list_by_project_applies_offset() -> None:
    """Skip the requested number of tasks."""
    session = create_test_session()
    project = create_project()

    tasks = [create_task(project.id) for _ in range(3)]
    session.add_all([project, *tasks])
    session.flush()

    repository = TaskRepository(session)

    all_tasks = repository.list_by_project(project.id)
    result = repository.list_by_project(project.id, offset=1)

    assert len(result) == 2
    assert [task.id for task in result] == [
        task.id for task in all_tasks[1:]
    ]

    session.close()


def test_list_by_project_returns_empty_list_when_no_tasks_match() -> None:
    """Return an empty list when no tasks match the filters."""
    session = create_test_session()
    project = create_project()
    task = create_task(project.id)
    session.add_all([project, task])
    session.flush()

    repository = TaskRepository(session)

    result = repository.list_by_project(
        project_id=project.id,
        status=TaskStatus.COMPLETED,
    )

    assert result == []

    session.close()
