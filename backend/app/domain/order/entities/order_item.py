from datetime import date
from uuid import UUID, uuid4

from app.domain.order.entities.order_hold import OrderHold
from app.domain.order.entities.receiving_record import ReceivingRecord
from app.domain.order.value_objects.hold_status import HoldStatus
from app.domain.order.value_objects.order_item_status import OrderItemStatus
from app.domain.shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class OrderItem:
    """訂單項目子實體。"""

    def __init__(
        self,
        item_number: int,
        material_name: str,
        model_name: str,
        specification: str = "",
        quantity: int = 1,
        unit_price: float = 0.0,
        delivery_date: date | None = None,
        status: OrderItemStatus = OrderItemStatus.PENDING,
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self._validate_material_name(material_name)
        self._validate_quantity(quantity)
        self._validate_price(unit_price)
        self.item_number = item_number
        self.material_name = material_name
        self.model_name = model_name
        self.specification = specification
        self.quantity = quantity
        self.unit_price = unit_price
        self.delivery_date = delivery_date
        self.status = status
        self.receiving_records: list[ReceivingRecord] = []
        self.holds: list[OrderHold] = []

    @staticmethod
    def _validate_material_name(name: str) -> None:
        if not name or not name.strip():
            raise BusinessRuleViolationError("Material name cannot be empty")
        if len(name) > 200:
            raise BusinessRuleViolationError("Material name cannot exceed 200 characters")

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        if quantity <= 0:
            raise BusinessRuleViolationError("Quantity must be greater than zero")

    @staticmethod
    def _validate_price(price: float) -> None:
        if price < 0:
            raise BusinessRuleViolationError("Unit price cannot be negative")

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

    @property
    def received_quantity(self) -> int:
        return sum(r.received_quantity for r in self.receiving_records)

    @property
    def active_hold_quantity(self) -> int:
        return sum(h.hold_quantity for h in self.holds if h.status == HoldStatus.ACTIVE)

    def add_receiving_record(self, record: ReceivingRecord) -> None:
        total_after = self.received_quantity + record.received_quantity
        if total_after > self.quantity:
            raise BusinessRuleViolationError(
                f"Total received ({total_after}) would exceed ordered quantity ({self.quantity})"
            )
        self.receiving_records.append(record)
        self._update_status()

    def add_hold(self, hold: OrderHold) -> None:
        available = self.quantity - self.active_hold_quantity
        if hold.hold_quantity > available:
            raise BusinessRuleViolationError(
                f"Hold quantity ({hold.hold_quantity}) exceeds available quantity ({available})"
            )
        self.holds.append(hold)

    def release_hold(self, hold_id: UUID, released_by: str) -> None:
        hold = self._find_hold(hold_id)
        hold.release(released_by)

    def _find_hold(self, hold_id: UUID) -> OrderHold:
        for hold in self.holds:
            if hold.id == hold_id:
                return hold
        raise EntityNotFoundError("OrderHold", hold_id)

    def _update_status(self) -> None:
        received = self.received_quantity
        if received == 0:
            self.status = OrderItemStatus.PENDING
        elif received < self.quantity:
            self.status = OrderItemStatus.PARTIALLY_RECEIVED
        else:
            self.status = OrderItemStatus.FULLY_RECEIVED

    def update(
        self,
        material_name: str | None = None,
        model_name: str | None = None,
        specification: str | None = None,
        quantity: int | None = None,
        unit_price: float | None = None,
        delivery_date: date | None = None,
    ) -> None:
        if material_name is not None:
            self._validate_material_name(material_name)
            self.material_name = material_name
        if model_name is not None:
            self.model_name = model_name
        if specification is not None:
            self.specification = specification
        if quantity is not None:
            self._validate_quantity(quantity)
            self.quantity = quantity
        if unit_price is not None:
            self._validate_price(unit_price)
            self.unit_price = unit_price
        if delivery_date is not None:
            self.delivery_date = delivery_date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderItem):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
