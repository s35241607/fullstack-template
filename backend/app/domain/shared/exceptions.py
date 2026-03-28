class DomainException(Exception):
    """Base class for all domain exceptions."""


class EntityNotFoundError(DomainException):
    """Raised when an entity cannot be found."""

    def __init__(self, entity_type: str, entity_id: object) -> None:
        super().__init__(f"{entity_type} with id '{entity_id}' not found")
        self.entity_type = entity_type
        self.entity_id = entity_id


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
