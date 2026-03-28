from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.bpmn.entities.process_definition import TaskType

# ── Task Definition ────────────────────────────────────────────────────────────

class TaskDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    task_type: TaskType
    position_x: float = 0.0
    position_y: float = 0.0
    config: dict = Field(default_factory=dict)


class TransitionDefinitionCreate(BaseModel):
    source_task_id: UUID
    target_task_id: UUID
    label: str = ""
    condition: str = ""


class TaskDefinitionResponse(BaseModel):
    id: UUID
    process_definition_id: UUID
    name: str
    task_type: str
    position_x: float
    position_y: float
    config: dict

    model_config = {"from_attributes": True}


class TransitionDefinitionResponse(BaseModel):
    id: UUID
    process_definition_id: UUID
    source_task_id: UUID
    target_task_id: UUID
    label: str
    condition: str

    model_config = {"from_attributes": True}


# ── Process Definition ─────────────────────────────────────────────────────────

class ProcessDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""


class ProcessDefinitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class ProcessDefinitionResponse(BaseModel):
    id: UUID
    name: str
    description: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    tasks: list[TaskDefinitionResponse] = []
    transitions: list[TransitionDefinitionResponse] = []

    model_config = {"from_attributes": True}


class ProcessDefinitionListItem(BaseModel):
    id: UUID
    name: str
    description: str
    version: int
    is_active: bool
    created_at: datetime
    task_count: int = 0

    model_config = {"from_attributes": True}


# ── Process Instance ───────────────────────────────────────────────────────────

class StartProcessRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    started_by: str = "system"
    variables: dict = Field(default_factory=dict)


class TaskInstanceResponse(BaseModel):
    id: UUID
    process_instance_id: UUID
    task_definition_id: UUID
    task_name: str
    task_type: str
    status: str
    assignee: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    form_data: dict

    model_config = {"from_attributes": True}


class CompleteTaskRequest(BaseModel):
    form_data: dict = Field(default_factory=dict)
    assignee: str = ""


class ProcessInstanceResponse(BaseModel):
    id: UUID
    process_definition_id: UUID
    name: str
    status: str
    started_by: str
    started_at: datetime
    completed_at: datetime | None
    variables: dict
    notes: str
    task_instances: list[TaskInstanceResponse] = []
    definition_name: str = ""

    model_config = {"from_attributes": True}
