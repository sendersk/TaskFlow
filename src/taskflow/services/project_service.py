
"""Application service for project operations."""

from datetime import UTC
from uuid import UUID

from sqlalchemy.orm import Session

from taskflow.domain.project import Project, ProjectStatus
from taskflow.models.project import ProjectModel
from taskflow.repositories.project_repository import ProjectRepository


class ProjectNotFoundError(LookupError):
    """Raised when a requested project does not exist."""


class ProjectService:
    """Coordinate project operations and database transactions."""

    def __init__(self, session: Session) -> None:
        """Initialize the service with a database session."""
        self._session = session
        self._repository = ProjectRepository(session)


    @staticmethod
    def _to_domain(model: ProjectModel) -> Project:
        """Convert a database model into a domain project."""
        created_at = model.created_at
        updated_at = model.updated_at

        # SQLite does not preserve timezone information in DateTime columns.
        # Database timestamps are stored in UTC, so restore the UTC timezone.
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=UTC)

        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            status=model.status,
            created_at=created_at,
            updated_at=updated_at,
        )


    @staticmethod
    def _to_model(project: Project) -> ProjectModel:
        """Convert a domain project into a database model."""
        return ProjectModel(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    def create(self, project: Project) -> Project:
        """Create and persist a project."""
        try:
            model = self._to_model(project)
            self._repository.create(model)
            self._session.commit()
            self._session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self._session.rollback()
            raise

    def get_by_id(self, project_id: UUID) -> Project | None:
        """Return a project by its ID."""
        model = self._repository.get_by_id(project_id)
        if model is None:
            return None

        return self._to_domain(model)

    def get_all(self) -> list[Project]:
        """Return all projects."""
        models = self._repository.get_all()
        return [self._to_domain(model) for model in models]

    def update_details(
        self,
        project_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Project:
        """Update project details."""
        try:
            model = self._repository.get_by_id(project_id)
            if model is None:
                raise ProjectNotFoundError(
                    f"Project with ID '{project_id}' was not found."
                )

            project = self._to_domain(model)
            project.update_details(name=name, description=description)

            model.name = project.name
            model.description = project.description
            model.updated_at = project.updated_at

            self._repository.update(model)
            self._session.commit()
            self._session.refresh(model)

            return self._to_domain(model)
        except Exception:
            self._session.rollback()
            raise

    def change_status(
        self,
        project_id: UUID,
        status: ProjectStatus,
    ) -> Project:
        """Change project status."""
        try:
            model = self._repository.get_by_id(project_id)
            if model is None:
                raise ProjectNotFoundError(
                    f"Project with ID '{project_id}' was not found."
                )

            project = self._to_domain(model)
            project.change_status(status)

            model.status = project.status
            model.updated_at = project.updated_at

            self._repository.update(model)
            self._session.commit()
            self._session.refresh(model)

            return self._to_domain(model)
        except Exception:
            self._session.rollback()
            raise

    def delete(self, project_id: UUID) -> None:
        """Delete a project by its ID."""
        try:
            model = self._repository.get_by_id(project_id)
            if model is None:
                raise ProjectNotFoundError(
                    f"Project with ID '{project_id}' was not found."
                )

            self._repository.delete(model)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
