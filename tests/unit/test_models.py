
"""Tests for SQLAlchemy persistence models."""

from sqlalchemy import Enum, ForeignKey

from taskflow.database.base import Base
from taskflow.domain.project import ProjectStatus
from taskflow.domain.task import TaskPriority, TaskStatus
from taskflow.models import ProjectModel, TaskModel


def test_project_model_uses_projects_table() -> None:
    """Map the project model to the projects table."""
    assert ProjectModel.__tablename__ == "projects"
    assert ProjectModel.__table__ in Base.metadata.tables.values()


def test_project_model_has_expected_columns() -> None:
    """Define all expected project columns."""
    expected_columns = {
        "id",
        "name",
        "description",
        "status",
        "created_at",
        "updated_at",
    }

    assert set(ProjectModel.__table__.columns.keys()) == expected_columns


def test_project_model_status_uses_project_status_enum() -> None:
    """Use the domain project status enum in persistence."""
    status_column = ProjectModel.__table__.columns["status"]

    assert isinstance(status_column.type, Enum)
    assert status_column.type.enum_class is ProjectStatus


def test_task_model_uses_tasks_table() -> None:
    """Map the task model to the tasks table."""
    assert TaskModel.__tablename__ == "tasks"
    assert TaskModel.__table__ in Base.metadata.tables.values()


def test_task_model_has_expected_columns() -> None:
    """Define all expected task columns."""
    expected_columns = {
        "id",
        "project_id",
        "title",
        "description",
        "status",
        "priority",
        "due_date",
        "created_at",
        "updated_at",
    }

    assert set(TaskModel.__table__.columns.keys()) == expected_columns


def test_task_model_project_id_references_projects() -> None:
    """Reference the projects table through a foreign key."""
    project_id_column = TaskModel.__table__.columns["project_id"]

    foreign_keys = list(project_id_column.foreign_keys)

    assert len(foreign_keys) == 1
    assert isinstance(foreign_keys[0], ForeignKey)
    assert foreign_keys[0].target_fullname == "projects.id"
    assert project_id_column.index is True


def test_task_model_status_uses_task_status_enum() -> None:
    """Use the domain task status enum in persistence."""
    status_column = TaskModel.__table__.columns["status"]

    assert isinstance(status_column.type, Enum)
    assert status_column.type.enum_class is TaskStatus


def test_task_model_priority_uses_task_priority_enum() -> None:
    """Use the domain task priority enum in persistence."""
    priority_column = TaskModel.__table__.columns["priority"]

    assert isinstance(priority_column.type, Enum)
    assert priority_column.type.enum_class is TaskPriority


def test_task_model_due_date_is_nullable() -> None:
    """Allow tasks without a due date."""
    due_date_column = TaskModel.__table__.columns["due_date"]

    assert due_date_column.nullable is True
