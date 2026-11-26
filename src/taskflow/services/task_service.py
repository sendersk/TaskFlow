
"""Application service for task operations."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from taskflow.domain.task import Task, TaskPriority, TaskStatus
from taskflow.models.task import TaskModel
from taskflow.repositories.task_repository import TaskRepository


class TaskNotFoundError(LookupError):
    """Raised when a requested task does not exist."""


class TaskService:
    """Coordinate task operations and database transactions."""

    def __init__(self, session: Session) -> None:
        """Initialize the service with a database session."""
        self._session = session
        self._repository = TaskRepository(session)

    @staticmethod
    def _ensure_timezone_aware(value: datetime) -> datetime:
        """Interpret naive database timestamps as UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    @classmethod
    def _to_domain(cls, model: TaskModel) -> Task:
        """Convert a database model into a domain task."""
        due_date = model.due_date
        if due_date is not None:
            due_date = cls._ensure_timezone_aware(due_date)

        return Task(
            id=model.id,
            project_id=model.project_id,
            title=model.title,
            description=model.description,
            status=model.status,
            priority=model.priority,
            due_date=due_date,
            created_at=cls._ensure_timezone_aware(model.created_at),
            updated_at=cls._ensure_timezone_aware(model.updated_at),
        )

    @staticmethod
    def _to_model(task: Task) -> TaskModel:
        """Convert a domain task into a database model."""
        return TaskModel(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def create(self, task: Task) -> Task:
        """Create and persist a task."""
        try:
            model = self._to_model(task)
            self._repository.create(model)
            self._session.commit()
            self._session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self._session.rollback()
            raise

    def get_by_id(self, task_id: UUID) -> Task | None:
        """Return a task by its ID."""
        model = self._repository.get_by_id(task_id)
        if model is None:
            return None
        return self._to_domain(model)

    def get_by_project_id(self, project_id: UUID) -> list[Task]:
        """Return all tasks belonging to a project."""
        models = self._repository.get_by_project_id(project_id)
        return [self._to_domain(model) for model in models]

    def list_by_project(
        self,
        project_id: UUID,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Task]:
        """Return filtered and paginated tasks for a project."""
        models = self._repository.list_by_project(
            project_id,
            status=status,
            priority=priority,
            limit=limit,
            offset=offset,
        )
        return [self._to_domain(model) for model in models]

    def update_details(
        self,
        task_id: UUID,
        *,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
    ) -> Task:
        """Update task details."""
        try:
            model = self._repository.get_by_id(task_id)
            if model is None:
                raise TaskNotFoundError(
                    f"Task with ID '{task_id}' was not found."
                )

            task = self._to_domain(model)
            task.update_details(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
            )

            model.title = task.title
            model.description = task.description
            model.priority = task.priority
            model.due_date = task.due_date
            model.updated_at = task.updated_at

            self._repository.update(model)
            self._session.commit()
            self._session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self._session.rollback()
            raise

    def change_status(
        self,
        task_id: UUID,
        status: TaskStatus,
    ) -> Task:
        """Change task status."""
        try:
            model = self._repository.get_by_id(task_id)
            if model is None:
                raise TaskNotFoundError(
                    f"Task with ID '{task_id}' was not found."
                )

            task = self._to_domain(model)
            task.change_status(status)

            model.status = task.status
            model.updated_at = task.updated_at

            self._repository.update(model)
            self._session.commit()
            self._session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self._session.rollback()
            raise

    def delete(self, task_id: UUID) -> None:
        """Delete a task by its ID."""
        try:
            model = self._repository.get_by_id(task_id)
            if model is None:
                raise TaskNotFoundError(
                    f"Task with ID '{task_id}' was not found."
                )

            self._repository.delete(model)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
