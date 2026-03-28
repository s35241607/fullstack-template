from abc import abstractmethod

from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.shared.repository import Repository


class ProcurementPlanRepository(Repository[ProcurementPlan]):
    """Repository interface for ProcurementPlan aggregate."""

    @abstractmethod
    async def get_all(self) -> list[ProcurementPlan]:
        """Retrieve all procurement plans."""
        ...
