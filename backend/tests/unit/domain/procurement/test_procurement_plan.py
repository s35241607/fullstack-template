from datetime import date

import pytest

from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.procurement.value_objects.plan_status import PlanStatus
from app.domain.shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class TestProcurementPlan:
    def test_create_plan_with_valid_data(self) -> None:
        plan = ProcurementPlan(name="Q1 Purchase", planned_date=date(2026, 6, 1))
        assert plan.name == "Q1 Purchase"
        assert plan.planned_date == date(2026, 6, 1)
        assert plan.status == PlanStatus.DRAFT
        assert plan.items == []
        assert plan.id is not None

    def test_create_plan_with_empty_name_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            ProcurementPlan(name="", planned_date=date(2026, 6, 1))

    def test_create_plan_with_name_too_long_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            ProcurementPlan(name="a" * 201, planned_date=date(2026, 6, 1))

    def test_update_draft_plan(self) -> None:
        plan = ProcurementPlan(name="Original", planned_date=date(2026, 6, 1))
        plan.update(name="Updated", planned_date=date(2026, 7, 1))
        assert plan.name == "Updated"
        assert plan.planned_date == date(2026, 7, 1)

    def test_update_submitted_plan_raises_error(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        plan.add_item(PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100))
        plan.submit()
        with pytest.raises(BusinessRuleViolationError):
            plan.update(name="New Name")

    def test_add_item_to_draft_plan(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        item = PlanItem(equipment_name="CNC", quantity=2, estimated_unit_price=50000)
        plan.add_item(item)
        assert len(plan.items) == 1
        assert plan.items[0].equipment_name == "CNC"

    def test_add_item_to_submitted_plan_raises_error(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        plan.add_item(PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100))
        plan.submit()
        with pytest.raises(BusinessRuleViolationError):
            plan.add_item(PlanItem(equipment_name="Another", quantity=1, estimated_unit_price=200))

    def test_remove_item_from_draft_plan(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        item = PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100)
        plan.add_item(item)
        plan.remove_item(item.id)
        assert len(plan.items) == 0

    def test_remove_item_from_submitted_plan_raises_error(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        item = PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100)
        plan.add_item(item)
        plan.submit()
        with pytest.raises(BusinessRuleViolationError):
            plan.remove_item(item.id)

    def test_remove_nonexistent_item_raises_error(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        from uuid import uuid4

        with pytest.raises(EntityNotFoundError):
            plan.remove_item(uuid4())

    def test_update_item_in_draft_plan(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        item = PlanItem(equipment_name="Old", quantity=1, estimated_unit_price=100)
        plan.add_item(item)
        updated = plan.update_item(item.id, equipment_name="New", quantity=5)
        assert updated.equipment_name == "New"
        assert updated.quantity == 5

    def test_update_item_in_submitted_plan_raises_error(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        item = PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100)
        plan.add_item(item)
        plan.submit()
        with pytest.raises(BusinessRuleViolationError):
            plan.update_item(item.id, equipment_name="New")

    def test_submit_plan_with_items(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        plan.add_item(PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100))
        plan.submit()
        assert plan.status == PlanStatus.SUBMITTED

    def test_submit_plan_without_items_raises_error(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        with pytest.raises(BusinessRuleViolationError):
            plan.submit()

    def test_submit_already_submitted_plan_raises_error(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        plan.add_item(PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100))
        plan.submit()
        with pytest.raises(BusinessRuleViolationError):
            plan.submit()

    def test_total_amount_calculation(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        plan.add_item(PlanItem(equipment_name="A", quantity=2, estimated_unit_price=1000))
        plan.add_item(PlanItem(equipment_name="B", quantity=3, estimated_unit_price=2000))
        assert plan.total_amount == 8000.0

    def test_total_amount_empty_plan(self) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2026, 6, 1))
        assert plan.total_amount == 0.0
