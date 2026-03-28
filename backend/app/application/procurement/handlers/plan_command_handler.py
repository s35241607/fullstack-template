from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.procurement.repositories.procurement_plan_repository import ProcurementPlanRepository
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class CreatePlanCommand:
    name: str
    planned_date: date


@dataclass
class UpdatePlanCommand:
    plan_id: UUID
    name: str | None = None
    planned_date: date | None = None


@dataclass
class DeletePlanCommand:
    plan_id: UUID


@dataclass
class SubmitPlanCommand:
    plan_id: UUID


class ProcurementPlanCommandHandler:
    """Handles write operations for ProcurementPlan aggregate."""

    def __init__(self, repository: ProcurementPlanRepository) -> None:
        self._repository = repository

    async def handle_create(self, command: CreatePlanCommand) -> ProcurementPlan:
        plan = ProcurementPlan(name=command.name, planned_date=command.planned_date)
        await self._repository.save(plan)
        return plan

    async def handle_update(self, command: UpdatePlanCommand) -> ProcurementPlan:
        plan = await self._repository.get_by_id(command.plan_id)
        if plan is None:
            raise EntityNotFoundError("ProcurementPlan", command.plan_id)
        plan.update(name=command.name, planned_date=command.planned_date)
        await self._repository.save(plan)
        return plan

    async def handle_delete(self, command: DeletePlanCommand) -> None:
        plan = await self._repository.get_by_id(command.plan_id)
        if plan is None:
            raise EntityNotFoundError("ProcurementPlan", command.plan_id)
        await self._repository.delete(command.plan_id)

    async def handle_submit(self, command: SubmitPlanCommand) -> ProcurementPlan:
        plan = await self._repository.get_by_id(command.plan_id)
        if plan is None:
            raise EntityNotFoundError("ProcurementPlan", command.plan_id)
        plan.submit()
        await self._repository.save(plan)
        return plan
