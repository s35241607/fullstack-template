from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.bpmn.entities.process_definition import TaskType
from app.infrastructure.database.models.process_definition_model import (
    ProcessDefinitionModel,
    TaskDefinitionModel,
    TransitionDefinitionModel,
)
from app.infrastructure.database.models.process_instance_model import (
    ProcessInstanceModel,
    TaskInstanceModel,
)
from app.infrastructure.database.session import get_db_session
from app.interfaces.api.v1.schemas.bpmn_schema import (
    CompleteTaskRequest,
    ProcessDefinitionCreate,
    ProcessDefinitionResponse,
    ProcessDefinitionUpdate,
    ProcessInstanceResponse,
    StartProcessRequest,
    TaskDefinitionCreate,
    TaskDefinitionResponse,
    TransitionDefinitionCreate,
    TransitionDefinitionResponse,
)

router = APIRouter(prefix="/bpmn", tags=["bpmn"])

# ── Helpers ────────────────────────────────────────────────────────────────────

def _def_to_response(m: ProcessDefinitionModel) -> ProcessDefinitionResponse:
    return ProcessDefinitionResponse(
        id=m.id,
        name=m.name,
        description=m.description,
        version=m.version,
        is_active=m.is_active,
        created_at=m.created_at,
        updated_at=m.updated_at,
        tasks=[
            TaskDefinitionResponse(
                id=t.id,
                process_definition_id=t.process_definition_id,
                name=t.name,
                task_type=t.task_type,
                position_x=t.position_x,
                position_y=t.position_y,
                config=t.config or {},
            )
            for t in m.tasks
        ],
        transitions=[
            TransitionDefinitionResponse(
                id=tr.id,
                process_definition_id=tr.process_definition_id,
                source_task_id=tr.source_task_id,
                target_task_id=tr.target_task_id,
                label=tr.label,
                condition=tr.condition,
            )
            for tr in m.transitions
        ],
    )


def _instance_to_response(m: ProcessInstanceModel) -> ProcessInstanceResponse:
    return ProcessInstanceResponse(
        id=m.id,
        process_definition_id=m.process_definition_id,
        name=m.name,
        status=m.status,
        started_by=m.started_by,
        started_at=m.started_at,
        completed_at=m.completed_at,
        variables=m.variables or {},
        notes=m.notes,
        definition_name=m.definition.name if m.definition else "",
        task_instances=[
            _task_to_response(t) for t in m.task_instances
        ],
    )


def _task_to_response(t: TaskInstanceModel) -> dict:  # type: ignore[return]
    from app.interfaces.api.v1.schemas.bpmn_schema import TaskInstanceResponse
    return TaskInstanceResponse(
        id=t.id,
        process_instance_id=t.process_instance_id,
        task_definition_id=t.task_definition_id,
        task_name=t.task_name,
        task_type=t.task_type,
        status=t.status,
        assignee=t.assignee,
        created_at=t.created_at,
        started_at=t.started_at,
        completed_at=t.completed_at,
        form_data=t.form_data or {},
    )


# ── Process Definitions ────────────────────────────────────────────────────────

@router.get("/definitions", response_model=list[ProcessDefinitionResponse])
async def list_definitions(
    db: AsyncSession = Depends(get_db_session),
) -> list[ProcessDefinitionResponse]:
    result = await db.execute(
        select(ProcessDefinitionModel)
        .options(
            selectinload(ProcessDefinitionModel.tasks),
            selectinload(ProcessDefinitionModel.transitions),
        )
        .order_by(ProcessDefinitionModel.created_at.desc())
    )
    return [_def_to_response(m) for m in result.scalars().all()]


@router.post("/definitions", response_model=ProcessDefinitionResponse, status_code=201)
async def create_definition(
    body: ProcessDefinitionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ProcessDefinitionResponse:
    model = ProcessDefinitionModel(
        id=uuid4(),
        name=body.name,
        description=body.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(model)
    await db.flush()
    await db.refresh(model, ["tasks", "transitions"])
    return _def_to_response(model)


@router.get("/definitions/{definition_id}", response_model=ProcessDefinitionResponse)
async def get_definition(
    definition_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ProcessDefinitionResponse:
    result = await db.execute(
        select(ProcessDefinitionModel)
        .where(ProcessDefinitionModel.id == definition_id)
        .options(
            selectinload(ProcessDefinitionModel.tasks),
            selectinload(ProcessDefinitionModel.transitions),
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process definition not found")
    return _def_to_response(model)


@router.patch("/definitions/{definition_id}", response_model=ProcessDefinitionResponse)
async def update_definition(
    definition_id: UUID,
    body: ProcessDefinitionUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> ProcessDefinitionResponse:
    result = await db.execute(
        select(ProcessDefinitionModel)
        .where(ProcessDefinitionModel.id == definition_id)
        .options(
            selectinload(ProcessDefinitionModel.tasks),
            selectinload(ProcessDefinitionModel.transitions),
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process definition not found")
    if body.name is not None:
        model.name = body.name
    if body.description is not None:
        model.description = body.description
    if body.is_active is not None:
        model.is_active = body.is_active
    model.updated_at = datetime.utcnow()
    return _def_to_response(model)


@router.delete("/definitions/{definition_id}", status_code=204)
async def delete_definition(
    definition_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    result = await db.execute(
        select(ProcessDefinitionModel).where(ProcessDefinitionModel.id == definition_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process definition not found")
    await db.delete(model)


# ── Tasks & Transitions ────────────────────────────────────────────────────────

@router.post("/definitions/{definition_id}/tasks", response_model=TaskDefinitionResponse, status_code=201)
async def add_task(
    definition_id: UUID,
    body: TaskDefinitionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> TaskDefinitionResponse:
    result = await db.execute(
        select(ProcessDefinitionModel).where(ProcessDefinitionModel.id == definition_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Process definition not found")

    task = TaskDefinitionModel(
        id=uuid4(),
        process_definition_id=definition_id,
        name=body.name,
        task_type=body.task_type.value,
        position_x=body.position_x,
        position_y=body.position_y,
        config=body.config,
    )
    db.add(task)
    await db.flush()
    return TaskDefinitionResponse(
        id=task.id,
        process_definition_id=task.process_definition_id,
        name=task.name,
        task_type=task.task_type,
        position_x=task.position_x,
        position_y=task.position_y,
        config=task.config or {},
    )


@router.post("/definitions/{definition_id}/transitions", response_model=TransitionDefinitionResponse, status_code=201)
async def add_transition(
    definition_id: UUID,
    body: TransitionDefinitionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> TransitionDefinitionResponse:
    transition = TransitionDefinitionModel(
        id=uuid4(),
        process_definition_id=definition_id,
        source_task_id=body.source_task_id,
        target_task_id=body.target_task_id,
        label=body.label,
        condition=body.condition,
    )
    db.add(transition)
    await db.flush()
    return TransitionDefinitionResponse(
        id=transition.id,
        process_definition_id=transition.process_definition_id,
        source_task_id=transition.source_task_id,
        target_task_id=transition.target_task_id,
        label=transition.label,
        condition=transition.condition,
    )


# ── Process Instances ──────────────────────────────────────────────────────────

@router.post("/definitions/{definition_id}/start", response_model=ProcessInstanceResponse, status_code=201)
async def start_instance(
    definition_id: UUID,
    body: StartProcessRequest,
    db: AsyncSession = Depends(get_db_session),
) -> ProcessInstanceResponse:
    result = await db.execute(
        select(ProcessDefinitionModel)
        .where(ProcessDefinitionModel.id == definition_id)
        .options(
            selectinload(ProcessDefinitionModel.tasks),
            selectinload(ProcessDefinitionModel.transitions),
        )
    )
    defn = result.scalar_one_or_none()
    if not defn:
        raise HTTPException(status_code=404, detail="Process definition not found")
    if not defn.is_active:
        raise HTTPException(status_code=400, detail="Process definition is not active")

    instance = ProcessInstanceModel(
        id=uuid4(),
        process_definition_id=definition_id,
        name=body.name,
        status="RUNNING",
        started_by=body.started_by,
        started_at=datetime.utcnow(),
        variables=body.variables,
    )
    db.add(instance)
    await db.flush()

    # Create task instances for all tasks (start with START_EVENT as ACTIVE, rest as PENDING)
    for task_def in defn.tasks:
        is_start = task_def.task_type == TaskType.START_EVENT.value
        ti = TaskInstanceModel(
            id=uuid4(),
            process_instance_id=instance.id,
            task_definition_id=task_def.id,
            task_name=task_def.name,
            task_type=task_def.task_type,
            status="ACTIVE" if is_start else "PENDING",
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow() if is_start else None,
        )
        db.add(ti)

    await db.flush()
    await db.refresh(instance, ["task_instances", "definition"])
    return _instance_to_response(instance)


@router.get("/instances", response_model=list[ProcessInstanceResponse])
async def list_instances(
    db: AsyncSession = Depends(get_db_session),
    status_filter: str | None = None,
) -> list[ProcessInstanceResponse]:
    query = (
        select(ProcessInstanceModel)
        .options(
            selectinload(ProcessInstanceModel.task_instances),
            selectinload(ProcessInstanceModel.definition),
        )
        .order_by(ProcessInstanceModel.started_at.desc())
    )
    if status_filter:
        query = query.where(ProcessInstanceModel.status == status_filter.upper())
    result = await db.execute(query)
    return [_instance_to_response(m) for m in result.scalars().all()]


@router.get("/instances/{instance_id}", response_model=ProcessInstanceResponse)
async def get_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ProcessInstanceResponse:
    result = await db.execute(
        select(ProcessInstanceModel)
        .where(ProcessInstanceModel.id == instance_id)
        .options(
            selectinload(ProcessInstanceModel.task_instances),
            selectinload(ProcessInstanceModel.definition),
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process instance not found")
    return _instance_to_response(model)


@router.post("/instances/{instance_id}/tasks/{task_instance_id}/complete", response_model=ProcessInstanceResponse)
async def complete_task(
    instance_id: UUID,
    task_instance_id: UUID,
    body: CompleteTaskRequest,
    db: AsyncSession = Depends(get_db_session),
) -> ProcessInstanceResponse:
    result = await db.execute(
        select(ProcessInstanceModel)
        .where(ProcessInstanceModel.id == instance_id)
        .options(
            selectinload(ProcessInstanceModel.task_instances),
            selectinload(ProcessInstanceModel.definition).selectinload(
                ProcessDefinitionModel.transitions
            ),
        )
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="Process instance not found")
    if instance.status != "RUNNING":
        raise HTTPException(status_code=400, detail="Process instance is not running")

    # Find and complete the task
    task = next((t for t in instance.task_instances if t.id == task_instance_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task instance not found")
    if task.status not in ("ACTIVE", "PENDING"):
        raise HTTPException(status_code=400, detail=f"Task is already {task.status}")

    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()
    if body.assignee:
        task.assignee = body.assignee
    if body.form_data:
        task.form_data = body.form_data

    # Activate downstream tasks based on transitions
    if instance.definition:
        outgoing = [
            tr for tr in instance.definition.transitions
            if tr.source_task_id == task.task_definition_id
        ]
        for transition in outgoing:
            next_task = next(
                (t for t in instance.task_instances
                 if t.task_definition_id == transition.target_task_id and t.status == "PENDING"),
                None,
            )
            if next_task:
                next_task.status = "ACTIVE"
                next_task.started_at = datetime.utcnow()

    # Check if all non-END tasks are done → complete the instance
    active_or_pending = [
        t for t in instance.task_instances
        if t.status in ("ACTIVE", "PENDING") and t.task_type != "END_EVENT"
    ]
    if not active_or_pending:
        instance.status = "COMPLETED"
        instance.completed_at = datetime.utcnow()
        # Mark END_EVENT tasks as completed too
        for t in instance.task_instances:
            if t.task_type == "END_EVENT" and t.status == "PENDING":
                t.status = "COMPLETED"
                t.completed_at = datetime.utcnow()

    await db.flush()
    await db.refresh(instance, ["task_instances", "definition"])
    return _instance_to_response(instance)


@router.post("/instances/{instance_id}/cancel", response_model=ProcessInstanceResponse)
async def cancel_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ProcessInstanceResponse:
    result = await db.execute(
        select(ProcessInstanceModel)
        .where(ProcessInstanceModel.id == instance_id)
        .options(
            selectinload(ProcessInstanceModel.task_instances),
            selectinload(ProcessInstanceModel.definition),
        )
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="Process instance not found")
    if instance.status != "RUNNING":
        raise HTTPException(status_code=400, detail="Only RUNNING instances can be cancelled")

    instance.status = "CANCELLED"
    instance.completed_at = datetime.utcnow()
    for t in instance.task_instances:
        if t.status in ("ACTIVE", "PENDING"):
            t.status = "SKIPPED"

    await db.flush()
    await db.refresh(instance, ["task_instances", "definition"])
    return _instance_to_response(instance)


@router.get("/tasks/active", response_model=list[dict])
async def list_active_tasks(
    assignee: str | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """Return all ACTIVE task instances across all running processes."""
    query = (
        select(TaskInstanceModel)
        .where(TaskInstanceModel.status == "ACTIVE")
        .order_by(TaskInstanceModel.started_at)
    )
    if assignee:
        query = query.where(TaskInstanceModel.assignee == assignee)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "process_instance_id": str(t.process_instance_id),
            "task_definition_id": str(t.task_definition_id),
            "task_name": t.task_name,
            "task_type": t.task_type,
            "status": t.status,
            "assignee": t.assignee,
            "created_at": t.created_at.isoformat(),
            "started_at": t.started_at.isoformat() if t.started_at else None,
        }
        for t in tasks
    ]
