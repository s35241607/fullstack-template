from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.order.entities.order_hold import OrderHold
from app.domain.order.entities.order_item import OrderItem
from app.domain.order.entities.purchase_order import PurchaseOrder
from app.domain.order.entities.receiving_record import ReceivingRecord
from app.domain.order.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.order.value_objects.hold_status import HoldStatus
from app.domain.order.value_objects.order_item_status import OrderItemStatus
from app.domain.order.value_objects.order_status import OrderStatus
from app.infrastructure.database.models.purchase_order_model import (
    OrderHoldModel,
    OrderItemModel,
    PurchaseOrderModel,
    ReceivingRecordModel,
)


class SqlAlchemyPurchaseOrderRepository(PurchaseOrderRepository):
    """SQLAlchemy implementation of PurchaseOrderRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> PurchaseOrder | None:
        result = await self._session.get(PurchaseOrderModel, entity_id)
        return self._to_entity(result) if result else None

    async def get_all(self, status: OrderStatus | None = None) -> list[PurchaseOrder]:
        stmt = select(PurchaseOrderModel)
        if status is not None:
            stmt = stmt.where(PurchaseOrderModel.status == status.value)
        stmt = stmt.order_by(PurchaseOrderModel.created_at.desc())
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_order_number(self, order_number: str) -> PurchaseOrder | None:
        stmt = select(PurchaseOrderModel).where(PurchaseOrderModel.order_number == order_number)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_holds_by_model(self, model_name: str) -> list[dict[str, object]]:
        stmt = (
            select(
                OrderHoldModel,
                OrderItemModel.material_name,
                OrderItemModel.model_name,
                OrderItemModel.quantity.label("ordered_quantity"),
                PurchaseOrderModel.order_number,
                PurchaseOrderModel.supplier_name,
            )
            .join(OrderItemModel, OrderHoldModel.order_item_id == OrderItemModel.id)
            .join(PurchaseOrderModel, OrderItemModel.order_id == PurchaseOrderModel.id)
            .where(OrderItemModel.model_name == model_name)
            .where(OrderHoldModel.status == HoldStatus.ACTIVE.value)
            .order_by(OrderHoldModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            {
                "hold_id": str(row[0].id),
                "hold_quantity": row[0].hold_quantity,
                "reason": row[0].reason,
                "held_by": row[0].held_by,
                "created_at": row[0].created_at.isoformat(),
                "material_name": row[1],
                "model_name": row[2],
                "ordered_quantity": row[3],
                "order_number": row[4],
                "supplier_name": row[5],
            }
            for row in rows
        ]

    async def get_all_model_hold_summary(self) -> list[dict[str, object]]:
        stmt = (
            select(
                OrderItemModel.model_name,
                func.sum(OrderHoldModel.hold_quantity).label("total_hold_quantity"),
                func.count(OrderHoldModel.id).label("hold_count"),
            )
            .join(OrderItemModel, OrderHoldModel.order_item_id == OrderItemModel.id)
            .where(OrderHoldModel.status == HoldStatus.ACTIVE.value)
            .group_by(OrderItemModel.model_name)
            .order_by(func.sum(OrderHoldModel.hold_quantity).desc())
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            {
                "model_name": row[0],
                "total_hold_quantity": int(row[1]),
                "hold_count": int(row[2]),
            }
            for row in rows
        ]

    async def save(self, entity: PurchaseOrder) -> None:
        existing = await self._session.get(PurchaseOrderModel, entity.id)
        if existing:
            existing.order_number = entity.order_number
            existing.supplier_name = entity.supplier_name
            existing.supplier_code = entity.supplier_code
            existing.order_date = entity.order_date
            existing.expected_delivery_date = entity.expected_delivery_date
            existing.notes = entity.notes
            existing.status = entity.status.value
            existing.updated_at = entity.updated_at
            self._sync_items(existing, entity)
        else:
            model = self._to_model(entity)
            self._session.add(model)

    def _sync_items(self, existing_model: PurchaseOrderModel, entity: PurchaseOrder) -> None:
        entity_item_ids = {item.id for item in entity.items}
        # Remove deleted items
        for item_model in list(existing_model.items):
            if item_model.id not in entity_item_ids:
                existing_model.items.remove(item_model)
        # Update or add items
        for item in entity.items:
            item_model = next((m for m in existing_model.items if m.id == item.id), None)
            if item_model:
                item_model.item_number = item.item_number
                item_model.material_name = item.material_name
                item_model.model_name = item.model_name
                item_model.specification = item.specification
                item_model.quantity = item.quantity
                item_model.unit_price = item.unit_price
                item_model.delivery_date = item.delivery_date
                item_model.status = item.status.value
                self._sync_receiving_records(item_model, item)
                self._sync_holds(item_model, item)
            else:
                existing_model.items.append(self._to_item_model(item, entity.id))

    def _sync_receiving_records(self, item_model: OrderItemModel, item: OrderItem) -> None:
        existing_ids = {r.id for r in item_model.receiving_records}
        for record in item.receiving_records:
            if record.id not in existing_ids:
                item_model.receiving_records.append(
                    ReceivingRecordModel(
                        id=record.id,
                        order_item_id=item.id,
                        received_quantity=record.received_quantity,
                        received_date=record.received_date,
                        inspector=record.inspector,
                        note=record.note,
                    )
                )

    def _sync_holds(self, item_model: OrderItemModel, item: OrderItem) -> None:
        entity_hold_ids = {h.id for h in item.holds}
        for hold_model in list(item_model.holds):
            if hold_model.id not in entity_hold_ids:
                item_model.holds.remove(hold_model)
        for hold in item.holds:
            hold_model = next((m for m in item_model.holds if m.id == hold.id), None)
            if hold_model:
                hold_model.hold_quantity = hold.hold_quantity
                hold_model.reason = hold.reason
                hold_model.status = hold.status.value
                hold_model.released_at = hold.released_at
                hold_model.released_by = hold.released_by
            else:
                item_model.holds.append(
                    OrderHoldModel(
                        id=hold.id,
                        order_item_id=item.id,
                        hold_quantity=hold.hold_quantity,
                        reason=hold.reason,
                        held_by=hold.held_by,
                        status=hold.status.value,
                        created_at=hold.created_at,
                        released_at=hold.released_at,
                        released_by=hold.released_by,
                    )
                )

    async def delete(self, entity_id: UUID) -> None:
        model = await self._session.get(PurchaseOrderModel, entity_id)
        if model:
            await self._session.delete(model)

    @staticmethod
    def _to_entity(model: PurchaseOrderModel) -> PurchaseOrder:
        order = PurchaseOrder.__new__(PurchaseOrder)
        order.id = model.id
        order.order_number = model.order_number
        order.supplier_name = model.supplier_name
        order.supplier_code = model.supplier_code
        order.order_date = model.order_date
        order.expected_delivery_date = model.expected_delivery_date
        order.notes = model.notes
        order.status = OrderStatus(model.status)
        order.created_at = model.created_at
        order.updated_at = model.updated_at
        order.items = [SqlAlchemyPurchaseOrderRepository._to_item_entity(item_model) for item_model in model.items]
        return order

    @staticmethod
    def _to_item_entity(model: OrderItemModel) -> OrderItem:
        item = OrderItem.__new__(OrderItem)
        item.id = model.id
        item.item_number = model.item_number
        item.material_name = model.material_name
        item.model_name = model.model_name
        item.specification = model.specification
        item.quantity = model.quantity
        item.unit_price = model.unit_price
        item.delivery_date = model.delivery_date
        item.status = OrderItemStatus(model.status)
        item.receiving_records = [
            SqlAlchemyPurchaseOrderRepository._to_receiving_entity(r) for r in model.receiving_records
        ]
        item.holds = [SqlAlchemyPurchaseOrderRepository._to_hold_entity(h) for h in model.holds]
        return item

    @staticmethod
    def _to_receiving_entity(model: ReceivingRecordModel) -> ReceivingRecord:
        record = ReceivingRecord.__new__(ReceivingRecord)
        record.id = model.id
        record.received_quantity = model.received_quantity
        record.received_date = model.received_date
        record.inspector = model.inspector
        record.note = model.note
        return record

    @staticmethod
    def _to_hold_entity(model: OrderHoldModel) -> OrderHold:
        hold = OrderHold.__new__(OrderHold)
        hold.id = model.id
        hold.hold_quantity = model.hold_quantity
        hold.reason = model.reason
        hold.held_by = model.held_by
        hold.status = HoldStatus(model.status)
        hold.created_at = model.created_at
        hold.released_at = model.released_at
        hold.released_by = model.released_by
        return hold

    @staticmethod
    def _to_model(entity: PurchaseOrder) -> PurchaseOrderModel:
        return PurchaseOrderModel(
            id=entity.id,
            order_number=entity.order_number,
            supplier_name=entity.supplier_name,
            supplier_code=entity.supplier_code,
            order_date=entity.order_date,
            expected_delivery_date=entity.expected_delivery_date,
            notes=entity.notes,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            items=[SqlAlchemyPurchaseOrderRepository._to_item_model(item, entity.id) for item in entity.items],
        )

    @staticmethod
    def _to_item_model(item: OrderItem, order_id: UUID) -> OrderItemModel:
        return OrderItemModel(
            id=item.id,
            order_id=order_id,
            item_number=item.item_number,
            material_name=item.material_name,
            model_name=item.model_name,
            specification=item.specification,
            quantity=item.quantity,
            unit_price=item.unit_price,
            delivery_date=item.delivery_date,
            status=item.status.value,
            receiving_records=[
                ReceivingRecordModel(
                    id=r.id,
                    order_item_id=item.id,
                    received_quantity=r.received_quantity,
                    received_date=r.received_date,
                    inspector=r.inspector,
                    note=r.note,
                )
                for r in item.receiving_records
            ],
            holds=[
                OrderHoldModel(
                    id=h.id,
                    order_item_id=item.id,
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
