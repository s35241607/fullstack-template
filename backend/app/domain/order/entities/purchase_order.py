from datetime import date, datetime
from uuid import UUID, uuid4

from app.domain.order.entities.order_item import OrderItem
from app.domain.order.value_objects.order_status import OrderStatus
from app.domain.shared.entity import Entity
from app.domain.shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class PurchaseOrder(Entity):
    """採購訂單聚合根。"""

    def __init__(
        self,
        order_number: str,
        supplier_name: str,
        order_date: date,
        expected_delivery_date: date,
        supplier_code: str = "",
        notes: str = "",
        status: OrderStatus = OrderStatus.OPEN,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        id: UUID | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._validate_order_number(order_number)
        self._validate_supplier_name(supplier_name)
        self.order_number = order_number
        self.supplier_name = supplier_name
        self.supplier_code = supplier_code
        self.order_date = order_date
        self.expected_delivery_date = expected_delivery_date
        self.notes = notes
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.items: list[OrderItem] = []

    @staticmethod
    def _validate_order_number(order_number: str) -> None:
        if not order_number or not order_number.strip():
            raise BusinessRuleViolationError("Order number cannot be empty")
        if len(order_number) > 50:
            raise BusinessRuleViolationError("Order number cannot exceed 50 characters")

    @staticmethod
    def _validate_supplier_name(name: str) -> None:
        if not name or not name.strip():
            raise BusinessRuleViolationError("Supplier name cannot be empty")
        if len(name) > 200:
            raise BusinessRuleViolationError("Supplier name cannot exceed 200 characters")

    def _ensure_open(self) -> None:
        if self.status in (OrderStatus.CLOSED, OrderStatus.CANCELLED):
            raise BusinessRuleViolationError("Cannot modify a closed or cancelled order")

    def update(
        self,
        supplier_name: str | None = None,
        expected_delivery_date: date | None = None,
        notes: str | None = None,
    ) -> None:
        self._ensure_open()
        if supplier_name is not None:
            self._validate_supplier_name(supplier_name)
            self.supplier_name = supplier_name
        if expected_delivery_date is not None:
            self.expected_delivery_date = expected_delivery_date
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.now()

    def add_item(self, item: OrderItem) -> None:
        self._ensure_open()
        self.items.append(item)
        self.updated_at = datetime.now()

    def find_item(self, item_id: UUID) -> OrderItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise EntityNotFoundError("OrderItem", item_id)

    def update_order_status(self) -> None:
        """依據所有項目的收料狀態更新訂單狀態。"""
        if not self.items:
            return
        all_received = all(item.received_quantity >= item.quantity for item in self.items)
        any_received = any(item.received_quantity > 0 for item in self.items)
        if all_received:
            self.status = OrderStatus.FULLY_RECEIVED
        elif any_received:
            self.status = OrderStatus.PARTIALLY_RECEIVED
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        if self.status == OrderStatus.CANCELLED:
            raise BusinessRuleViolationError("Order is already cancelled")
        if self.status in (OrderStatus.FULLY_RECEIVED, OrderStatus.CLOSED):
            raise BusinessRuleViolationError("Cannot cancel a fully received or closed order")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()

    def close(self) -> None:
        if self.status == OrderStatus.CLOSED:
            raise BusinessRuleViolationError("Order is already closed")
        if self.status != OrderStatus.FULLY_RECEIVED:
            raise BusinessRuleViolationError("Can only close a fully received order")
        self.status = OrderStatus.CLOSED
        self.updated_at = datetime.now()

    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def total_received(self) -> int:
        return sum(item.received_quantity for item in self.items)

    @property
    def total_ordered(self) -> int:
        return sum(item.quantity for item in self.items)
