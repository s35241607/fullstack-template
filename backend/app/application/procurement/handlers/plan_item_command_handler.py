from dataclasses import dataclass
from uuid import UUID

from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.procurement.repositories.procurement_plan_repository import ProcurementPlanRepository
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class AddItemCommand:
    plan_id: UUID
    equipment_name: str
    specification: str = ""
    quantity: int = 1
    estimated_unit_price: float = 0.0
    note: str = ""


@dataclass
class UpdateItemCommand:
    plan_id: UUID
    item_id: UUID
    equipment_name: str | None = None
    specification: str | None = None
    quantity: int | None = None
    estimated_unit_price: float | None = None
    note: str | None = None


@dataclass
class RemoveItemCommand:
    plan_id: UUID
    item_id: UUID


class PlanItemCommandHandler:
    """Handles write operations for PlanItem within a ProcurementPlan."""

    def __init__(self, repository: ProcurementPlanRepository) -> None:
        self._repository = repository

    async def _get_plan(self, plan_id: UUID) -> ProcurementPlan:
        plan = await self._repository.get_by_id(plan_id)
        if plan is None:
            raise EntityNotFoundError("ProcurementPlan", plan_id)
        return plan

    async def handle_add(self, command: AddItemCommand) -> PlanItem:
        plan = await self._get_plan(command.plan_id)
        item = PlanItem(
            equipment_name=command.equipment_name,
            specification=command.specification,
            quantity=command.quantity,
            estimated_unit_price=command.estimated_unit_price,
            note=command.note,
        )
        plan.add_item(item)
        await self._repository.save(plan)
        return item

    async def handle_update(self, command: UpdateItemCommand) -> PlanItem:
        plan = await self._get_plan(command.plan_id)
        item = plan.update_item(
            command.item_id,
            equipment_name=command.equipment_name,
            specification=command.specification,
            quantity=command.quantity,
            estimated_unit_price=command.estimated_unit_price,
            note=command.note,
        )
        await self._repository.save(plan)
        return item

    async def handle_remove(self, command: RemoveItemCommand) -> None:
        plan = await self._get_plan(command.plan_id)
        plan.remove_item(command.item_id)
        await self._repository.save(plan)
