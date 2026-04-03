from datetime import datetime
from uuid import UUID, uuid4

from app.domain.order.value_objects.hold_status import HoldStatus
from app.domain.shared.exceptions import BusinessRuleViolationError


class OrderHold:
    """訂單項目 On-Hold 子實體。"""

    def __init__(
        self,
        hold_quantity: int,
        reason: str,
        held_by: str,
        status: HoldStatus = HoldStatus.ACTIVE,
        created_at: datetime | None = None,
        released_at: datetime | None = None,
        released_by: str | None = None,
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self._validate_quantity(hold_quantity)
        self._validate_reason(reason)
        self.hold_quantity = hold_quantity
        self.reason = reason
        self.held_by = held_by
        self.status = status
        self.created_at = created_at or datetime.now()
        self.released_at = released_at
        self.released_by = released_by

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        if quantity <= 0:
            raise BusinessRuleViolationError("Hold quantity must be greater than zero")

    @staticmethod
    def _validate_reason(reason: str) -> None:
        if not reason or not reason.strip():
            raise BusinessRuleViolationError("Hold reason cannot be empty")

    def release(self, released_by: str) -> None:
        if self.status != HoldStatus.ACTIVE:
            raise BusinessRuleViolationError("Can only release an active hold")
        self.status = HoldStatus.RELEASED
        self.released_at = datetime.now()
        self.released_by = released_by

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderHold):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
