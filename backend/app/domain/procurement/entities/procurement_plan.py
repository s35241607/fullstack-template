from datetime import date
from uuid import UUID

from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.procurement.value_objects.plan_status import PlanStatus
from app.domain.shared.entity import Entity
from app.domain.shared.exceptions import BusinessRuleViolationError


class ProcurementPlan(Entity):
    """採購計畫聚合根。"""

    def __init__(
        self,
        name: str,
        planned_date: date,
        status: PlanStatus = PlanStatus.DRAFT,
    ) -> None:
        super().__init__()
        self._validate_name(name)
        self.name = name
        self.planned_date = planned_date
        self.status = status
        self.items: list[PlanItem] = []

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise BusinessRuleViolationError("Plan name cannot be empty")
        if len(name) > 200:
            raise BusinessRuleViolationError("Plan name cannot exceed 200 characters")

    def _ensure_draft(self) -> None:
        if self.status != PlanStatus.DRAFT:
            raise BusinessRuleViolationError("Cannot modify a submitted plan")

    def update(self, name: str | None = None, planned_date: date | None = None) -> None:
        self._ensure_draft()
        if name is not None:
            self._validate_name(name)
            self.name = name
        if planned_date is not None:
            self.planned_date = planned_date

    def add_item(self, item: PlanItem) -> None:
        self._ensure_draft()
        self.items.append(item)

    def update_item(
        self,
        item_id: UUID,
        **kwargs: str | int | float | None,
    ) -> PlanItem:
        self._ensure_draft()
        item = self._find_item(item_id)
        item.update(**kwargs)  # type: ignore[arg-type]
        return item

    def remove_item(self, item_id: UUID) -> None:
        self._ensure_draft()
        item = self._find_item(item_id)
        self.items.remove(item)

    def submit(self) -> None:
        if self.status != PlanStatus.DRAFT:
            raise BusinessRuleViolationError("Plan is already submitted")
        if not self.items:
            raise BusinessRuleViolationError("Cannot submit a plan without items")
        self.status = PlanStatus.SUBMITTED

    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)

    def _find_item(self, item_id: UUID) -> PlanItem:
        for item in self.items:
            if item.id == item_id:
                return item
        from app.domain.shared.exceptions import EntityNotFoundError

        raise EntityNotFoundError("PlanItem", item_id)
