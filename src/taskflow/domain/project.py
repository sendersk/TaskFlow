
"""Project domain model."""

from dataclasses import dataclass
from dataclasses import field as dataclass_field
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
    id: UUID = dataclass_field(default_factory=uuid4)
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = dataclass_field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = dataclass_field(
        default_factory=lambda: datetime.now(UTC)
    )
