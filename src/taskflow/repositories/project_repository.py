
"""Repository for project persistence operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskflow.models.project import ProjectModel


class ProjectRepository:
    """Handle database operations for projects."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def get_by_id(self, project_id: UUID) -> ProjectModel | None:
        """Return a project by its ID."""
        statement = select(ProjectModel).where(ProjectModel.id == project_id)
        return self._session.scalar(statement)

    def get_all(self) -> list[ProjectModel]:
        """Return all projects."""
        statement = select(ProjectModel).order_by(ProjectModel.created_at.desc())
        return list(self._session.scalars(statement).all())

    def create(self, project: ProjectModel) -> ProjectModel:
        """Add a project to the current transaction."""
        self._session.add(project)
        self._session.flush()
        return project

    def update(self, project: ProjectModel) -> ProjectModel:
        """Persist changes to an existing project."""
        self._session.add(project)
        self._session.flush()
        return project

    def delete(self, project: ProjectModel) -> None:
        """Delete a project from the current transaction."""
        self._session.delete(project)
        self._session.flush()
