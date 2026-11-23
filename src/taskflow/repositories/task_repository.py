
"""Repository for task persistence operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskflow.domain.task import TaskPriority, TaskStatus
from taskflow.models.task import TaskModel


class TaskRepository:
    """Handle database operations for tasks."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def get_by_id(self, task_id: UUID) -> TaskModel | None:
        """Return a task by its ID."""
        statement = select(TaskModel).where(TaskModel.id == task_id)
        return self._session.scalar(statement)

    def get_by_project_id(self, project_id: UUID) -> list[TaskModel]:
        """Return all tasks belonging to a project."""
        return self.list_by_project(
            project_id=project_id,
            limit=100,
            offset=0,
        )

    def list_by_project(
        self,
        project_id: UUID,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TaskModel]:
        """Return filtered and paginated tasks for a project."""
        statement = select(TaskModel).where(
            TaskModel.project_id == project_id
        )

        if status is not None:
            statement = statement.where(TaskModel.status == status)

        if priority is not None:
            statement = statement.where(TaskModel.priority == priority)

        statement = (
            statement
            .order_by(
                TaskModel.created_at.desc(),
                TaskModel.id.asc(),
            )
            .limit(limit)
            .offset(offset)
        )

        return list(self._session.scalars(statement).all())

    def create(self, task: TaskModel) -> TaskModel:
        """Add a task to the current transaction."""
        self._session.add(task)
        self._session.flush()
        return task

    def update(self, task: TaskModel) -> TaskModel:
        """Persist changes to an existing task."""
        self._session.add(task)
        self._session.flush()
        return task

    def delete(self, task: TaskModel) -> None:
        """Delete a task from the current transaction."""
        self._session.delete(task)
        self._session.flush()
