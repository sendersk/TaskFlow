
"""Task domain model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class TaskStatus(StrEnum):
    """Available task statuses."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class TaskPriority(StrEnum):
    """Available task priorities."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Task:
    """Represent a task in TaskFlow."""

    project_id: UUID
    title: str
    description: str = ""
    id: UUID = field(default_factory=uuid4)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate task data after initialization."""
        self.title = self.title.strip()
        self.description = self.description.strip()

        if not self.title:
            raise ValueError("Task title cannot be empty.")

        if self.due_date is not None and self.due_date.tzinfo is None:
            raise ValueError("Task due date must be timezone-aware.")

        if self.created_at.tzinfo is None:
            raise ValueError("Task creation timestamp must be timezone-aware.")

        if self.updated_at.tzinfo is None:
            raise ValueError("Task update timestamp must be timezone-aware.")

    def update_details(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
    ) -> None:
        """Update task details."""
        if title is not None:
            normalized_title = title.strip()
            if not normalized_title:
                raise ValueError("Task title cannot be empty.")
            self.title = normalized_title

        if description is not None:
            self.description = description.strip()

        if priority is not None:
            self.priority = priority

        if due_date is not None:
            if due_date.tzinfo is None:
                raise ValueError("Task due date must be timezone-aware.")
            self.due_date = due_date

        self.updated_at = datetime.now(UTC)
