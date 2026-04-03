from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.procurement.repositories.procurement_plan_repository import ProcurementPlanRepository
from app.domain.procurement.value_objects.plan_status import PlanItemStatus, PlanStatus
from app.infrastructure.database.models.procurement_plan_model import PlanItemModel, ProcurementPlanModel


class SqlAlchemyProcurementPlanRepository(ProcurementPlanRepository):
    """SQLAlchemy implementation of ProcurementPlanRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> ProcurementPlan | None:
        result = await self._session.get(ProcurementPlanModel, entity_id)
        return self._to_entity(result) if result else None

    async def get_all(self) -> list[ProcurementPlan]:
        result = await self._session.execute(select(ProcurementPlanModel))
        return [self._to_entity(model) for model in result.scalars().all()]

    async def save(self, entity: ProcurementPlan) -> None:
        existing = await self._session.get(ProcurementPlanModel, entity.id)
        if existing:
            existing.name = entity.name
            existing.planned_date = entity.planned_date
            existing.status = entity.status.value

            # Sync items: remove deleted, update existing, add new
            entity_item_ids = {item.id for item in entity.items}

            # Delete removed items
            for item_model in list(existing.items):
                if item_model.id not in entity_item_ids:
                    existing.items.remove(item_model)

            # Update or add items
            for item in entity.items:
                item_model = next((m for m in existing.items if m.id == item.id), None)
                if item_model:
                    item_model.equipment_name = item.equipment_name
                    item_model.specification = item.specification
                    item_model.quantity = item.quantity
                    item_model.estimated_unit_price = item.estimated_unit_price
                    item_model.note = item.note
                    item_model.item_status = item.item_status.value
                    item_model.spec_file_url = item.spec_file_url
                    item_model.spec_uploaded_by = item.spec_uploaded_by
                    item_model.spec_uploaded_at = item.spec_uploaded_at
                    item_model.supplier_name = item.supplier_name
                    item_model.quoted_unit_price = item.quoted_unit_price
                    item_model.quoted_at = item.quoted_at
                else:
                    existing.items.append(self._to_item_model(item, entity.id))
        else:
            model = self._to_model(entity)
            self._session.add(model)

    async def delete(self, entity_id: UUID) -> None:
        model = await self._session.get(ProcurementPlanModel, entity_id)
        if model:
            await self._session.delete(model)

    @staticmethod
    def _to_entity(model: ProcurementPlanModel) -> ProcurementPlan:
        plan = ProcurementPlan.__new__(ProcurementPlan)
        plan.id = model.id
        plan.name = model.name
        plan.planned_date = model.planned_date
        plan.status = PlanStatus(model.status)
        plan.items = [SqlAlchemyProcurementPlanRepository._to_item_entity(item_model) for item_model in model.items]
        return plan

    @staticmethod
    def _to_item_entity(model: PlanItemModel) -> PlanItem:
        item = PlanItem.__new__(PlanItem)
        item.id = model.id
        item.equipment_name = model.equipment_name
        item.specification = model.specification
        item.quantity = model.quantity
        item.estimated_unit_price = model.estimated_unit_price
        item.note = model.note
        item.item_status = PlanItemStatus(model.item_status)
        item.spec_file_url = model.spec_file_url
        item.spec_uploaded_by = model.spec_uploaded_by
        item.spec_uploaded_at = model.spec_uploaded_at
        item.supplier_name = model.supplier_name
        item.quoted_unit_price = model.quoted_unit_price
        item.quoted_at = model.quoted_at
        return item

    @staticmethod
    def _to_model(entity: ProcurementPlan) -> ProcurementPlanModel:
        return ProcurementPlanModel(
            id=entity.id,
            name=entity.name,
            planned_date=entity.planned_date,
            status=entity.status.value,
            items=[SqlAlchemyProcurementPlanRepository._to_item_model(item, entity.id) for item in entity.items],
        )

    @staticmethod
    def _to_item_model(item: PlanItem, plan_id: UUID) -> PlanItemModel:
        return PlanItemModel(
            id=item.id,
            plan_id=plan_id,
            equipment_name=item.equipment_name,
            specification=item.specification,
            quantity=item.quantity,
            estimated_unit_price=item.estimated_unit_price,
            note=item.note,
            item_status=item.item_status.value,
            spec_file_url=item.spec_file_url,
            spec_uploaded_by=item.spec_uploaded_by,
            spec_uploaded_at=item.spec_uploaded_at,
            supplier_name=item.supplier_name,
            quoted_unit_price=item.quoted_unit_price,
            quoted_at=item.quoted_at,
        )
