from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Entity:
    """Base class for all Domain Entities."""

    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
