import pytest

from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.shared.exceptions import BusinessRuleViolationError


class TestPlanItem:
    def test_create_item_with_valid_data(self) -> None:
        item = PlanItem(equipment_name="CNC Machine", specification="5-axis", quantity=2, estimated_unit_price=50000.0)
        assert item.equipment_name == "CNC Machine"
        assert item.specification == "5-axis"
        assert item.quantity == 2
        assert item.estimated_unit_price == 50000.0
        assert item.note == ""
        assert item.id is not None

    def test_create_item_with_empty_name_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            PlanItem(equipment_name="")

    def test_create_item_with_whitespace_name_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            PlanItem(equipment_name="   ")

    def test_create_item_with_name_too_long_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            PlanItem(equipment_name="a" * 201)

    def test_create_item_with_zero_quantity_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            PlanItem(equipment_name="Machine", quantity=0)

    def test_create_item_with_negative_quantity_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            PlanItem(equipment_name="Machine", quantity=-1)

    def test_create_item_with_negative_price_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            PlanItem(equipment_name="Machine", estimated_unit_price=-100.0)

    def test_create_item_with_zero_price_is_allowed(self) -> None:
        item = PlanItem(equipment_name="Machine", estimated_unit_price=0.0)
        assert item.estimated_unit_price == 0.0

    def test_subtotal_calculation(self) -> None:
        item = PlanItem(equipment_name="Machine", quantity=3, estimated_unit_price=10000.0)
        assert item.subtotal == 30000.0

    def test_update_item(self) -> None:
        item = PlanItem(equipment_name="Old", quantity=1, estimated_unit_price=100.0)
        item.update(equipment_name="New", quantity=5, estimated_unit_price=200.0, note="Updated")
        assert item.equipment_name == "New"
        assert item.quantity == 5
        assert item.estimated_unit_price == 200.0
        assert item.note == "Updated"

    def test_update_with_invalid_name_raises_error(self) -> None:
        item = PlanItem(equipment_name="Machine")
        with pytest.raises(BusinessRuleViolationError):
            item.update(equipment_name="")

    def test_update_with_invalid_quantity_raises_error(self) -> None:
        item = PlanItem(equipment_name="Machine")
        with pytest.raises(BusinessRuleViolationError):
            item.update(quantity=0)

    def test_update_with_negative_price_raises_error(self) -> None:
        item = PlanItem(equipment_name="Machine")
        with pytest.raises(BusinessRuleViolationError):
            item.update(estimated_unit_price=-1.0)
