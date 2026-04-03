from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.order.handlers.order_command_handler import (
    AddOrderItemCommand,
    CancelOrderCommand,
    CloseOrderCommand,
    CreateOrderCommand,
    DeleteOrderCommand,
    OrderCommandHandler,
    UpdateOrderCommand,
    UpdateOrderItemCommand,
)
from app.application.order.handlers.order_item_action_handler import (
    AddHoldCommand,
    AddReceivingRecordCommand,
    OrderItemActionHandler,
    ReleaseHoldCommand,
)
from app.application.order.handlers.order_query_handler import (
    GetHoldsByModelQuery,
    GetOrderQuery,
    ListModelHoldSummaryQuery,
    ListOrdersQuery,
    OrderQueryHandler,
)
from app.domain.order.entities.order_item import OrderItem
from app.domain.order.entities.purchase_order import PurchaseOrder
from app.domain.shared.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.infrastructure.database.repositories.sqlalchemy_purchase_order_repository import (
    SqlAlchemyPurchaseOrderRepository,
)
from app.infrastructure.database.session import get_db_session
from app.interfaces.api.v1.schemas.order_schema import (
    ModelHoldDetailResponse,
    ModelHoldSummaryResponse,
    OrderHoldCreateRequest,
    OrderHoldReleaseRequest,
    OrderHoldResponse,
    OrderItemCreateRequest,
    OrderItemResponse,
    OrderItemUpdateRequest,
    PurchaseOrderCreateRequest,
    PurchaseOrderResponse,
    PurchaseOrderUpdateRequest,
    ReceivingRecordCreateRequest,
    ReceivingRecordResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


# ── Dependency Factories ──────────────────────────────────────────────────────


def _get_repository(session: AsyncSession) -> SqlAlchemyPurchaseOrderRepository:
    return SqlAlchemyPurchaseOrderRepository(session)


def get_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> OrderCommandHandler:
    return OrderCommandHandler(_get_repository(session))


def get_query_handler(
    session: AsyncSession = Depends(get_db_session),
) -> OrderQueryHandler:
    return OrderQueryHandler(_get_repository(session))


def get_item_action_handler(
    session: AsyncSession = Depends(get_db_session),
) -> OrderItemActionHandler:
    return OrderItemActionHandler(_get_repository(session))


# ── Entity → Response Converters ──────────────────────────────────────────────


def _item_to_response(item: OrderItem) -> OrderItemResponse:
    return OrderItemResponse(
        id=item.id,
        item_number=item.item_number,
        material_name=item.material_name,
        model_name=item.model_name,
        specification=item.specification,
        quantity=item.quantity,
        unit_price=item.unit_price,
        delivery_date=item.delivery_date,
        status=item.status.value,
        received_quantity=item.received_quantity,
        active_hold_quantity=item.active_hold_quantity,
        subtotal=item.subtotal,
        receiving_records=[
            ReceivingRecordResponse(
                id=r.id,
                received_quantity=r.received_quantity,
                received_date=r.received_date,
                inspector=r.inspector,
                note=r.note,
            )
            for r in item.receiving_records
        ],
        holds=[
            OrderHoldResponse(
                id=h.id,
                hold_quantity=h.hold_quantity,
                reason=h.reason,
                held_by=h.held_by,
                status=h.status.value,
                created_at=h.created_at,
                released_at=h.released_at,
                released_by=h.released_by,
            )
            for h in item.holds
        ],
    )


def _order_to_response(order: PurchaseOrder) -> PurchaseOrderResponse:
    return PurchaseOrderResponse(
        id=order.id,
        order_number=order.order_number,
        supplier_name=order.supplier_name,
        supplier_code=order.supplier_code,
        order_date=order.order_date,
        expected_delivery_date=order.expected_delivery_date,
        notes=order.notes,
        status=order.status.value,
        total_amount=order.total_amount,
        total_ordered=order.total_ordered,
        total_received=order.total_received,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[_item_to_response(item) for item in order.items],
    )


# ── Order Endpoints ──────────────────────────────────────────────────────────


@router.get("/", response_model=list[PurchaseOrderResponse])
async def list_orders(
    status_filter: str | None = Query(default=None, alias="status"),
    handler: OrderQueryHandler = Depends(get_query_handler),
) -> list[PurchaseOrderResponse]:
    orders = await handler.handle_list(ListOrdersQuery(status=status_filter))
    return [_order_to_response(o) for o in orders]


@router.get("/hold-summary", response_model=list[ModelHoldSummaryResponse])
async def list_model_hold_summary(
    handler: OrderQueryHandler = Depends(get_query_handler),
) -> list[ModelHoldSummaryResponse]:
    """取得所有機型的 On-Hold 數量總覽。"""
    result = await handler.handle_model_hold_summary(ListModelHoldSummaryQuery())
    return [ModelHoldSummaryResponse(**row) for row in result]


@router.get("/holds-by-model/{model_name}", response_model=list[ModelHoldDetailResponse])
async def get_holds_by_model(
    model_name: str,
    handler: OrderQueryHandler = Depends(get_query_handler),
) -> list[ModelHoldDetailResponse]:
    """取得指定機型的所有 On-Hold 明細。"""
    result = await handler.handle_holds_by_model(GetHoldsByModelQuery(model_name=model_name))
    return [ModelHoldDetailResponse(**row) for row in result]


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
async def get_order(
    order_id: UUID,
    handler: OrderQueryHandler = Depends(get_query_handler),
) -> PurchaseOrderResponse:
    try:
        order = await handler.handle_get(GetOrderQuery(order_id=order_id))
        return _order_to_response(order)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: PurchaseOrderCreateRequest,
    handler: OrderCommandHandler = Depends(get_command_handler),
) -> PurchaseOrderResponse:
    try:
        order = await handler.handle_create(
            CreateOrderCommand(
                order_number=body.order_number,
                supplier_name=body.supplier_name,
                order_date=body.order_date,
                expected_delivery_date=body.expected_delivery_date,
                supplier_code=body.supplier_code,
                notes=body.notes,
            )
        )
        return _order_to_response(order)
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.patch("/{order_id}", response_model=PurchaseOrderResponse)
async def update_order(
    order_id: UUID,
    body: PurchaseOrderUpdateRequest,
    handler: OrderCommandHandler = Depends(get_command_handler),
) -> PurchaseOrderResponse:
    try:
        order = await handler.handle_update(
            UpdateOrderCommand(
                order_id=order_id,
                supplier_name=body.supplier_name,
                expected_delivery_date=body.expected_delivery_date,
                notes=body.notes,
            )
        )
        return _order_to_response(order)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    handler: OrderCommandHandler = Depends(get_command_handler),
) -> None:
    try:
        await handler.handle_delete(DeleteOrderCommand(order_id=order_id))
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/{order_id}/cancel", response_model=PurchaseOrderResponse)
async def cancel_order(
    order_id: UUID,
    handler: OrderCommandHandler = Depends(get_command_handler),
) -> PurchaseOrderResponse:
    try:
        order = await handler.handle_cancel(CancelOrderCommand(order_id=order_id))
        return _order_to_response(order)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.post("/{order_id}/close", response_model=PurchaseOrderResponse)
async def close_order(
    order_id: UUID,
    handler: OrderCommandHandler = Depends(get_command_handler),
) -> PurchaseOrderResponse:
    try:
        order = await handler.handle_close(CloseOrderCommand(order_id=order_id))
        return _order_to_response(order)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


# ── Order Item Endpoints ─────────────────────────────────────────────────────


@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def add_order_item(
    order_id: UUID,
    body: OrderItemCreateRequest,
    handler: OrderCommandHandler = Depends(get_command_handler),
) -> OrderItemResponse:
    try:
        item = await handler.handle_add_item(
            AddOrderItemCommand(
                order_id=order_id,
                item_number=body.item_number,
                material_name=body.material_name,
                model_name=body.model_name,
                specification=body.specification,
                quantity=body.quantity,
                unit_price=body.unit_price,
                delivery_date=body.delivery_date,
            )
        )
        return _item_to_response(item)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    order_id: UUID,
    item_id: UUID,
    body: OrderItemUpdateRequest,
    handler: OrderCommandHandler = Depends(get_command_handler),
) -> OrderItemResponse:
    try:
        item = await handler.handle_update_item(
            UpdateOrderItemCommand(
                order_id=order_id,
                item_id=item_id,
                material_name=body.material_name,
                model_name=body.model_name,
                specification=body.specification,
                quantity=body.quantity,
                unit_price=body.unit_price,
                delivery_date=body.delivery_date,
            )
        )
        return _item_to_response(item)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


# ── Receiving Record Endpoints ───────────────────────────────────────────────


@router.post(
    "/{order_id}/items/{item_id}/receiving",
    response_model=ReceivingRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_receiving_record(
    order_id: UUID,
    item_id: UUID,
    body: ReceivingRecordCreateRequest,
    handler: OrderItemActionHandler = Depends(get_item_action_handler),
) -> ReceivingRecordResponse:
    try:
        record = await handler.handle_add_receiving(
            AddReceivingRecordCommand(
                order_id=order_id,
                item_id=item_id,
                received_quantity=body.received_quantity,
                received_date=body.received_date,
                inspector=body.inspector,
                note=body.note,
            )
        )
        return ReceivingRecordResponse(
            id=record.id,
            received_quantity=record.received_quantity,
            received_date=record.received_date,
            inspector=record.inspector,
            note=record.note,
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


# ── Hold Endpoints ───────────────────────────────────────────────────────────


@router.post(
    "/{order_id}/items/{item_id}/holds",
    response_model=OrderHoldResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_hold(
    order_id: UUID,
    item_id: UUID,
    body: OrderHoldCreateRequest,
    handler: OrderItemActionHandler = Depends(get_item_action_handler),
) -> OrderHoldResponse:
    try:
        hold = await handler.handle_add_hold(
            AddHoldCommand(
                order_id=order_id,
                item_id=item_id,
                hold_quantity=body.hold_quantity,
                reason=body.reason,
                held_by=body.held_by,
            )
        )
        return OrderHoldResponse(
            id=hold.id,
            hold_quantity=hold.hold_quantity,
            reason=hold.reason,
            held_by=hold.held_by,
            status=hold.status.value,
            created_at=hold.created_at,
            released_at=hold.released_at,
            released_by=hold.released_by,
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.post("/{order_id}/items/{item_id}/holds/{hold_id}/release", status_code=status.HTTP_204_NO_CONTENT)
async def release_hold(
    order_id: UUID,
    item_id: UUID,
    hold_id: UUID,
    body: OrderHoldReleaseRequest,
    handler: OrderItemActionHandler = Depends(get_item_action_handler),
) -> None:
    try:
        await handler.handle_release_hold(
            ReleaseHoldCommand(
                order_id=order_id,
                item_id=item_id,
                hold_id=hold_id,
                released_by=body.released_by,
            )
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
