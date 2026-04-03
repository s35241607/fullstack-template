from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.order.entities.order_hold import OrderHold
from app.domain.order.entities.receiving_record import ReceivingRecord
from app.domain.order.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class AddReceivingRecordCommand:
    order_id: UUID
    item_id: UUID
    received_quantity: int
    received_date: datetime
    inspector: str = ""
    note: str = ""


@dataclass
class AddHoldCommand:
    order_id: UUID
    item_id: UUID
    hold_quantity: int
    reason: str
    held_by: str


@dataclass
class ReleaseHoldCommand:
    order_id: UUID
    item_id: UUID
    hold_id: UUID
    released_by: str


class OrderItemActionHandler:
    """處理訂單項目的收料和 On-Hold 操作。"""

    def __init__(self, repository: PurchaseOrderRepository) -> None:
        self._repository = repository

    async def handle_add_receiving(self, command: AddReceivingRecordCommand) -> ReceivingRecord:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        item = order.find_item(command.item_id)
        record = ReceivingRecord(
            received_quantity=command.received_quantity,
            received_date=command.received_date,
            inspector=command.inspector,
            note=command.note,
        )
        item.add_receiving_record(record)
        order.update_order_status()
        await self._repository.save(order)
        return record

    async def handle_add_hold(self, command: AddHoldCommand) -> OrderHold:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        item = order.find_item(command.item_id)
        hold = OrderHold(
            hold_quantity=command.hold_quantity,
            reason=command.reason,
            held_by=command.held_by,
        )
        item.add_hold(hold)
        await self._repository.save(order)
        return hold

    async def handle_release_hold(self, command: ReleaseHoldCommand) -> None:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        item = order.find_item(command.item_id)
        item.release_hold(command.hold_id, command.released_by)
        await self._repository.save(order)
