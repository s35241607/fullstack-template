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


@dataclass
class UploadSpecCommand:
    plan_id: UUID
    item_id: UUID
    file_url: str
    uploaded_by: str


@dataclass
class SetQuoteCommand:
    plan_id: UUID
    item_id: UUID
    quoted_unit_price: float
    supplier_name: str


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

    async def handle_upload_spec(self, command: UploadSpecCommand) -> PlanItem:
        plan = await self._get_plan(command.plan_id)
        item = self._find_item(plan, command.item_id)
        item.upload_spec(command.file_url, command.uploaded_by)
        await self._repository.save(plan)
        return item

    async def handle_set_quote(self, command: SetQuoteCommand) -> PlanItem:
        plan = await self._get_plan(command.plan_id)
        item = self._find_item(plan, command.item_id)
        item.set_quote(command.quoted_unit_price, command.supplier_name)
        await self._repository.save(plan)
        return item

    @staticmethod
    def _find_item(plan: ProcurementPlan, item_id: UUID) -> PlanItem:
        for item in plan.items:
            if item.id == item_id:
                return item
        raise EntityNotFoundError("PlanItem", item_id)
