from datetime import datetime
from uuid import UUID

from app.domain.bpmn.entities.process_definition import ProcessStatus, TaskStatus


class TaskInstance:
    def __init__(
        self,
        id: UUID,
        process_instance_id: UUID,
        task_definition_id: UUID,
        task_name: str,
        task_type: str,
        status: TaskStatus = TaskStatus.PENDING,
        assignee: str = "",
        created_at: datetime | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        form_data: dict | None = None,
    ) -> None:
        self.id = id
        self.process_instance_id = process_instance_id
        self.task_definition_id = task_definition_id
        self.task_name = task_name
        self.task_type = task_type
        self.status = status
        self.assignee = assignee
        self.created_at = created_at or datetime.utcnow()
        self.started_at = started_at
        self.completed_at = completed_at
        self.form_data: dict = form_data or {}


class ProcessInstance:
    def __init__(
        self,
        id: UUID,
        process_definition_id: UUID,
        name: str,
        status: ProcessStatus = ProcessStatus.RUNNING,
        started_by: str = "",
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        variables: dict | None = None,
        task_instances: list[TaskInstance] | None = None,
        definition_name: str = "",
    ) -> None:
        self.id = id
        self.process_definition_id = process_definition_id
        self.name = name
        self.status = status
        self.started_by = started_by
        self.started_at = started_at or datetime.utcnow()
        self.completed_at = completed_at
        self.variables: dict = variables or {}
        self.task_instances: list[TaskInstance] = task_instances or []
        self.definition_name = definition_name
