
"""Project domain model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class ProjectStatus(StrEnum):
    """Available project statuses."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"



@dataclass(slots=True)
class Project:
    """Represent a project in TaskFlow."""

    name: str
    description: str = ""
    id: UUID = field(default_factory=uuid4)
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate project data after initialization."""
        self.name = self.name.strip()
        self.description = self.description.strip()

        if not self.name:
            raise ValueError("Project name cannot be empty.")

        if self.created_at.tzinfo is None:
            raise ValueError("Project creation timestamp must be timezone-aware.")

        if self.updated_at.tzinfo is None:
            raise ValueError("Project update timestamp must be timezone-aware.")

    def update_details(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update project details."""
        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("Project name cannot be empty.")
            self.name = normalized_name

        if description is not None:
            self.description = description.strip()

        self.updated_at = datetime.now(UTC)

