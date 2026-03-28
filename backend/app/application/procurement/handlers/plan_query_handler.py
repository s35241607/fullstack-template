from dataclasses import dataclass
from uuid import UUID

from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.procurement.repositories.procurement_plan_repository import ProcurementPlanRepository
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class GetPlanQuery:
    plan_id: UUID


@dataclass
class ListPlansQuery:
    pass


class ProcurementPlanQueryHandler:
    """Handles read operations for ProcurementPlan aggregate."""

    def __init__(self, repository: ProcurementPlanRepository) -> None:
        self._repository = repository

    async def handle_get(self, query: GetPlanQuery) -> ProcurementPlan:
        plan = await self._repository.get_by_id(query.plan_id)
        if plan is None:
            raise EntityNotFoundError("ProcurementPlan", query.plan_id)
        return plan

    async def handle_list(self, query: ListPlansQuery) -> list[ProcurementPlan]:  # noqa: ARG002
        return await self._repository.get_all()
