from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Base class for all Value Objects.

    Value Objects are immutable and compared by value, not identity.
    """
