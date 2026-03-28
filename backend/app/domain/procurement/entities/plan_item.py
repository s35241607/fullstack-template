from uuid import UUID, uuid4

from app.domain.shared.exceptions import BusinessRuleViolationError


class PlanItem:
    """計畫項目子實體，代表採購計畫中的一筆機台設備。"""

    def __init__(
        self,
        equipment_name: str,
        specification: str = "",
        quantity: int = 1,
        estimated_unit_price: float = 0.0,
        note: str = "",
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self._validate_equipment_name(equipment_name)
        self._validate_quantity(quantity)
        self._validate_price(estimated_unit_price)
        self.equipment_name = equipment_name
        self.specification = specification
        self.quantity = quantity
        self.estimated_unit_price = estimated_unit_price
        self.note = note

    @staticmethod
    def _validate_equipment_name(name: str) -> None:
        if not name or not name.strip():
            raise BusinessRuleViolationError("Equipment name cannot be empty")
        if len(name) > 200:
            raise BusinessRuleViolationError("Equipment name cannot exceed 200 characters")

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        if quantity <= 0:
            raise BusinessRuleViolationError("Quantity must be greater than zero")

    @staticmethod
    def _validate_price(price: float) -> None:
        if price < 0:
            raise BusinessRuleViolationError("Estimated unit price cannot be negative")

    def update(
        self,
        equipment_name: str | None = None,
        specification: str | None = None,
        quantity: int | None = None,
        estimated_unit_price: float | None = None,
        note: str | None = None,
    ) -> None:
        if equipment_name is not None:
            self._validate_equipment_name(equipment_name)
            self.equipment_name = equipment_name
        if specification is not None:
            self.specification = specification
        if quantity is not None:
            self._validate_quantity(quantity)
            self.quantity = quantity
        if estimated_unit_price is not None:
            self._validate_price(estimated_unit_price)
            self.estimated_unit_price = estimated_unit_price
        if note is not None:
            self.note = note

    @property
    def subtotal(self) -> float:
        return self.quantity * self.estimated_unit_price

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlanItem):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
