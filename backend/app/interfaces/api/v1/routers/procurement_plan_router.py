from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.procurement.handlers.plan_command_handler import (
    ApprovePlanCommand,
    CreatePlanCommand,
    DeletePlanCommand,
    MarkQuotedCommand,
    ProcurementPlanCommandHandler,
    SendToEeReviewCommand,
    SubmitPlanCommand,
    SubmitToBudgetCommand,
    UpdatePlanCommand,
)
from app.application.procurement.handlers.plan_item_command_handler import (
    AddItemCommand,
    PlanItemCommandHandler,
    RemoveItemCommand,
    SetQuoteCommand,
    UpdateItemCommand,
    UploadSpecCommand,
)
from app.application.procurement.handlers.plan_query_handler import (
    GetPlanQuery,
    ListPlansQuery,
    ProcurementPlanQueryHandler,
)
from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.shared.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.infrastructure.database.repositories.sqlalchemy_procurement_plan_repository import (
    SqlAlchemyProcurementPlanRepository,
)
from app.infrastructure.database.session import get_db_session
from app.interfaces.api.v1.schemas.procurement_plan_schema import (
    PlanItemCreateRequest,
    PlanItemResponse,
    PlanItemUpdateRequest,
    ProcurementPlanCreateRequest,
    ProcurementPlanResponse,
    ProcurementPlanUpdateRequest,
    SetQuoteRequest,
    UploadSpecRequest,
)

router = APIRouter(prefix="/procurement-plans", tags=["procurement-plans"])


def _get_repository(session: AsyncSession) -> SqlAlchemyProcurementPlanRepository:
    return SqlAlchemyProcurementPlanRepository(session)


def get_plan_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> ProcurementPlanCommandHandler:
    return ProcurementPlanCommandHandler(_get_repository(session))


def get_plan_item_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> PlanItemCommandHandler:
    return PlanItemCommandHandler(_get_repository(session))


def get_plan_query_handler(
    session: AsyncSession = Depends(get_db_session),
) -> ProcurementPlanQueryHandler:
    return ProcurementPlanQueryHandler(_get_repository(session))


def _item_to_response(item: PlanItem) -> PlanItemResponse:
    return PlanItemResponse(
        id=item.id,
        equipment_name=item.equipment_name,
        specification=item.specification,
        quantity=item.quantity,
        estimated_unit_price=item.estimated_unit_price,
        note=item.note,
        item_status=item.item_status.value,
        spec_file_url=item.spec_file_url,
        spec_uploaded_by=item.spec_uploaded_by,
        spec_uploaded_at=item.spec_uploaded_at,
        supplier_name=item.supplier_name,
        quoted_unit_price=item.quoted_unit_price,
        quoted_at=item.quoted_at,
        subtotal=item.subtotal,
        final_subtotal=item.final_subtotal,
    )


def _plan_to_response(plan: ProcurementPlan) -> ProcurementPlanResponse:
    return ProcurementPlanResponse(
        id=plan.id,
        name=plan.name,
        planned_date=plan.planned_date,
        status=plan.status.value,
        total_amount=plan.total_amount,
        items=[_item_to_response(item) for item in plan.items],
    )


@router.get("/", response_model=list[ProcurementPlanResponse])
async def list_plans(
    handler: ProcurementPlanQueryHandler = Depends(get_plan_query_handler),
) -> list[ProcurementPlanResponse]:
    plans = await handler.handle_list(ListPlansQuery())
    return [_plan_to_response(p) for p in plans]


@router.get("/{plan_id}", response_model=ProcurementPlanResponse)
async def get_plan(
    plan_id: UUID,
    handler: ProcurementPlanQueryHandler = Depends(get_plan_query_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_get(GetPlanQuery(plan_id=plan_id))
        return _plan_to_response(plan)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/", response_model=ProcurementPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    body: ProcurementPlanCreateRequest,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_create(CreatePlanCommand(name=body.name, planned_date=body.planned_date))
        return _plan_to_response(plan)
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.patch("/{plan_id}", response_model=ProcurementPlanResponse)
async def update_plan(
    plan_id: UUID,
    body: ProcurementPlanUpdateRequest,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_update(
            UpdatePlanCommand(plan_id=plan_id, name=body.name, planned_date=body.planned_date)
        )
        return _plan_to_response(plan)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: UUID,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> None:
    try:
        await handler.handle_delete(DeletePlanCommand(plan_id=plan_id))
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/{plan_id}/submit", response_model=ProcurementPlanResponse)
async def submit_plan(
    plan_id: UUID,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_submit(SubmitPlanCommand(plan_id=plan_id))
        return _plan_to_response(plan)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


# --- Plan Item endpoints ---


@router.post("/{plan_id}/items", response_model=PlanItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    plan_id: UUID,
    body: PlanItemCreateRequest,
    handler: PlanItemCommandHandler = Depends(get_plan_item_command_handler),
) -> PlanItemResponse:
    try:
        item = await handler.handle_add(
            AddItemCommand(
                plan_id=plan_id,
                equipment_name=body.equipment_name,
                specification=body.specification,
                quantity=body.quantity,
                estimated_unit_price=body.estimated_unit_price,
                note=body.note,
            )
        )
        return _item_to_response(item)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.patch("/{plan_id}/items/{item_id}", response_model=PlanItemResponse)
async def update_item(
    plan_id: UUID,
    item_id: UUID,
    body: PlanItemUpdateRequest,
    handler: PlanItemCommandHandler = Depends(get_plan_item_command_handler),
) -> PlanItemResponse:
    try:
        item = await handler.handle_update(
            UpdateItemCommand(
                plan_id=plan_id,
                item_id=item_id,
                equipment_name=body.equipment_name,
                specification=body.specification,
                quantity=body.quantity,
                estimated_unit_price=body.estimated_unit_price,
                note=body.note,
            )
        )
        return _item_to_response(item)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.delete("/{plan_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    plan_id: UUID,
    item_id: UUID,
    handler: PlanItemCommandHandler = Depends(get_plan_item_command_handler),
) -> None:
    try:
        await handler.handle_remove(RemoveItemCommand(plan_id=plan_id, item_id=item_id))
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


# --- Workflow endpoints ---


@router.post("/{plan_id}/ee-review", response_model=ProcurementPlanResponse)
async def send_to_ee_review(
    plan_id: UUID,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_send_to_ee_review(SendToEeReviewCommand(plan_id=plan_id))
        return _plan_to_response(plan)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.post("/{plan_id}/mark-quoted", response_model=ProcurementPlanResponse)
async def mark_quoted(
    plan_id: UUID,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_mark_quoted(MarkQuotedCommand(plan_id=plan_id))
        return _plan_to_response(plan)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.post("/{plan_id}/approve", response_model=ProcurementPlanResponse)
async def approve_plan(
    plan_id: UUID,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_approve(ApprovePlanCommand(plan_id=plan_id))
        return _plan_to_response(plan)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.post("/{plan_id}/submit-budget", response_model=ProcurementPlanResponse)
async def submit_to_budget(
    plan_id: UUID,
    handler: ProcurementPlanCommandHandler = Depends(get_plan_command_handler),
) -> ProcurementPlanResponse:
    try:
        plan = await handler.handle_submit_to_budget(SubmitToBudgetCommand(plan_id=plan_id))
        return _plan_to_response(plan)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


# --- Item SPEC / Quote endpoints ---


@router.post("/{plan_id}/items/{item_id}/upload-spec", response_model=PlanItemResponse)
async def upload_spec(
    plan_id: UUID,
    item_id: UUID,
    body: UploadSpecRequest,
    handler: PlanItemCommandHandler = Depends(get_plan_item_command_handler),
) -> PlanItemResponse:
    try:
        item = await handler.handle_upload_spec(
            UploadSpecCommand(
                plan_id=plan_id,
                item_id=item_id,
                file_url=body.file_url,
                uploaded_by=body.uploaded_by,
            )
        )
        return _item_to_response(item)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.post("/{plan_id}/items/{item_id}/set-quote", response_model=PlanItemResponse)
async def set_quote(
    plan_id: UUID,
    item_id: UUID,
    body: SetQuoteRequest,
    handler: PlanItemCommandHandler = Depends(get_plan_item_command_handler),
) -> PlanItemResponse:
    try:
        item = await handler.handle_set_quote(
            SetQuoteCommand(
                plan_id=plan_id,
                item_id=item_id,
                quoted_unit_price=body.quoted_unit_price,
                supplier_name=body.supplier_name,
            )
        )
        return _item_to_response(item)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
