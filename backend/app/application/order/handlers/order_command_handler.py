from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.domain.order.entities.order_item import OrderItem
from app.domain.order.entities.purchase_order import PurchaseOrder
from app.domain.order.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class CreateOrderCommand:
    order_number: str
    supplier_name: str
    order_date: date
    expected_delivery_date: date
    supplier_code: str = ""
    notes: str = ""


@dataclass
class UpdateOrderCommand:
    order_id: UUID
    supplier_name: str | None = None
    expected_delivery_date: date | None = None
    notes: str | None = None


@dataclass
class DeleteOrderCommand:
    order_id: UUID


@dataclass
class CancelOrderCommand:
    order_id: UUID


@dataclass
class CloseOrderCommand:
    order_id: UUID


@dataclass
class AddOrderItemCommand:
    order_id: UUID
    item_number: int
    material_name: str
    model_name: str
    specification: str = ""
    quantity: int = 1
    unit_price: float = 0.0
    delivery_date: date | None = None


@dataclass
class UpdateOrderItemCommand:
    order_id: UUID
    item_id: UUID
    material_name: str | None = None
    model_name: str | None = None
    specification: str | None = None
    quantity: int | None = None
    unit_price: float | None = None
    delivery_date: date | None = None


class OrderCommandHandler:
    """訂單寫入 handler。"""

    def __init__(self, repository: PurchaseOrderRepository) -> None:
        self._repository = repository

    async def handle_create(self, command: CreateOrderCommand) -> PurchaseOrder:
        order = PurchaseOrder(
            order_number=command.order_number,
            supplier_name=command.supplier_name,
            order_date=command.order_date,
            expected_delivery_date=command.expected_delivery_date,
            supplier_code=command.supplier_code,
            notes=command.notes,
        )
        await self._repository.save(order)
        return order

    async def handle_update(self, command: UpdateOrderCommand) -> PurchaseOrder:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        order.update(
            supplier_name=command.supplier_name,
            expected_delivery_date=command.expected_delivery_date,
            notes=command.notes,
        )
        await self._repository.save(order)
        return order

    async def handle_delete(self, command: DeleteOrderCommand) -> None:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        await self._repository.delete(command.order_id)

    async def handle_cancel(self, command: CancelOrderCommand) -> PurchaseOrder:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        order.cancel()
        await self._repository.save(order)
        return order

    async def handle_close(self, command: CloseOrderCommand) -> PurchaseOrder:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        order.close()
        await self._repository.save(order)
        return order

    async def handle_add_item(self, command: AddOrderItemCommand) -> OrderItem:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        item = OrderItem(
            item_number=command.item_number,
            material_name=command.material_name,
            model_name=command.model_name,
            specification=command.specification,
            quantity=command.quantity,
            unit_price=command.unit_price,
            delivery_date=command.delivery_date,
        )
        order.add_item(item)
        await self._repository.save(order)
        return item

    async def handle_update_item(self, command: UpdateOrderItemCommand) -> OrderItem:
        order = await self._repository.get_by_id(command.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", command.order_id)
        item = order.find_item(command.item_id)
        item.update(
            material_name=command.material_name,
            model_name=command.model_name,
            specification=command.specification,
            quantity=command.quantity,
            unit_price=command.unit_price,
            delivery_date=command.delivery_date,
        )
        await self._repository.save(order)
        return item
