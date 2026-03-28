from datetime import datetime
from enum import StrEnum
from uuid import UUID


class TaskType(StrEnum):
    START_EVENT = "START_EVENT"
    END_EVENT = "END_EVENT"
    USER_TASK = "USER_TASK"
    SERVICE_TASK = "SERVICE_TASK"
    EXCLUSIVE_GATEWAY = "EXCLUSIVE_GATEWAY"
    PARALLEL_GATEWAY = "PARALLEL_GATEWAY"


class ProcessStatus(StrEnum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class TaskDefinition:
    def __init__(
        self,
        id: UUID,
        process_definition_id: UUID,
        name: str,
        task_type: TaskType,
        position_x: float = 0.0,
        position_y: float = 0.0,
        config: dict | None = None,
    ) -> None:
        self.id = id
        self.process_definition_id = process_definition_id
        self.name = name
        self.task_type = task_type
        self.position_x = position_x
        self.position_y = position_y
        self.config: dict = config or {}


class TransitionDefinition:
    def __init__(
        self,
        id: UUID,
        process_definition_id: UUID,
        source_task_id: UUID,
        target_task_id: UUID,
        label: str = "",
        condition: str = "",
    ) -> None:
        self.id = id
        self.process_definition_id = process_definition_id
        self.source_task_id = source_task_id
        self.target_task_id = target_task_id
        self.label = label
        self.condition = condition


class ProcessDefinition:
    def __init__(
        self,
        id: UUID,
        name: str,
        description: str = "",
        version: int = 1,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        tasks: list[TaskDefinition] | None = None,
        transitions: list[TransitionDefinition] | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.version = version
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.tasks: list[TaskDefinition] = tasks or []
        self.transitions: list[TransitionDefinition] = transitions or []
