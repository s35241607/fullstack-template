from datetime import datetime
from uuid import UUID, uuid4

from app.domain.procurement.value_objects.plan_status import PlanItemStatus
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
        item_status: PlanItemStatus = PlanItemStatus.PENDING,
        spec_file_url: str | None = None,
        spec_uploaded_by: str | None = None,
        spec_uploaded_at: datetime | None = None,
        supplier_name: str | None = None,
        quoted_unit_price: float | None = None,
        quoted_at: datetime | None = None,
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
        self.item_status = item_status
        self.spec_file_url = spec_file_url
        self.spec_uploaded_by = spec_uploaded_by
        self.spec_uploaded_at = spec_uploaded_at
        self.supplier_name = supplier_name
        self.quoted_unit_price = quoted_unit_price
        self.quoted_at = quoted_at

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

    @property
    def final_subtotal(self) -> float:
        """以供應商報價計算的小計（無報價則用預估價）。"""
        price = self.quoted_unit_price if self.quoted_unit_price is not None else self.estimated_unit_price
        return self.quantity * price

    def upload_spec(self, file_url: str, uploaded_by: str) -> None:
        if not file_url or not file_url.strip():
            raise BusinessRuleViolationError("Spec file URL cannot be empty")
        self.spec_file_url = file_url
        self.spec_uploaded_by = uploaded_by
        self.spec_uploaded_at = datetime.now()
        self.item_status = PlanItemStatus.SPEC_UPLOADED

    def set_quote(self, quoted_unit_price: float, supplier_name: str) -> None:
        if quoted_unit_price < 0:
            raise BusinessRuleViolationError("Quoted price cannot be negative")
        if not supplier_name or not supplier_name.strip():
            raise BusinessRuleViolationError("Supplier name cannot be empty")
        self.quoted_unit_price = quoted_unit_price
        self.supplier_name = supplier_name
        self.quoted_at = datetime.now()
        self.item_status = PlanItemStatus.QUOTED

    def approve(self) -> None:
        if self.item_status not in (PlanItemStatus.QUOTED, PlanItemStatus.SPEC_UPLOADED):
            raise BusinessRuleViolationError("Item must be quoted or spec uploaded to approve")
        self.item_status = PlanItemStatus.APPROVED

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlanItem):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
