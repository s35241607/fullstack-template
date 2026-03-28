from app.domain.shared.entity import Entity
from app.domain.shared.exceptions import BusinessRuleViolationError


class Item(Entity):
    """Item domain entity."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__()
        self._validate_name(name)
        self.name = name
        self.description = description

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise BusinessRuleViolationError("Item name cannot be empty")
        if len(name) > 100:
            raise BusinessRuleViolationError("Item name cannot exceed 100 characters")

    def update(self, name: str | None = None, description: str | None = None) -> None:
        """Update item fields with validation."""
        if name is not None:
            self._validate_name(name)
            self.name = name
        if description is not None:
            self.description = description
