from datetime import datetime
from uuid import UUID, uuid4

from app.domain.shared.exceptions import BusinessRuleViolationError


class ReceivingRecord:
    """收料紀錄子實體。"""

    def __init__(
        self,
        received_quantity: int,
        received_date: datetime,
        inspector: str = "",
        note: str = "",
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self._validate_quantity(received_quantity)
        self.received_quantity = received_quantity
        self.received_date = received_date
        self.inspector = inspector
        self.note = note

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        if quantity <= 0:
            raise BusinessRuleViolationError("Received quantity must be greater than zero")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReceivingRecord):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
