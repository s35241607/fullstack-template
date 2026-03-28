from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.procurement.handlers.plan_item_command_handler import (
    AddItemCommand,
    PlanItemCommandHandler,
    RemoveItemCommand,
    UpdateItemCommand,
)
from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.shared.exceptions import EntityNotFoundError


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_repository: AsyncMock) -> PlanItemCommandHandler:
    return PlanItemCommandHandler(mock_repository)


@pytest.fixture
def draft_plan() -> ProcurementPlan:
    return ProcurementPlan(name="Test Plan", planned_date=date(2025, 6, 1))


class TestAddItem:
    async def test_add_item(
        self, handler: PlanItemCommandHandler, mock_repository: AsyncMock, draft_plan: ProcurementPlan
    ) -> None:
        mock_repository.get_by_id.return_value = draft_plan
        command = AddItemCommand(
            plan_id=draft_plan.id,
            equipment_name="CNC Machine",
            specification="5-axis",
            quantity=2,
            estimated_unit_price=50000.0,
        )
        item = await handler.handle_add(command)

        assert item.equipment_name == "CNC Machine"
        assert item.quantity == 2
        assert len(draft_plan.items) == 1
        mock_repository.save.assert_called_once_with(draft_plan)

    async def test_add_item_to_nonexistent_plan_raises_error(
        self, handler: PlanItemCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None
        command = AddItemCommand(plan_id=uuid4(), equipment_name="Machine")

        with pytest.raises(EntityNotFoundError):
            await handler.handle_add(command)


class TestUpdateItem:
    async def test_update_item(
        self, handler: PlanItemCommandHandler, mock_repository: AsyncMock, draft_plan: ProcurementPlan
    ) -> None:
        item = PlanItem(equipment_name="Old Name", quantity=1, estimated_unit_price=100.0)
        draft_plan.add_item(item)
        mock_repository.get_by_id.return_value = draft_plan

        command = UpdateItemCommand(plan_id=draft_plan.id, item_id=item.id, equipment_name="New Name", quantity=5)
        updated = await handler.handle_update(command)

        assert updated.equipment_name == "New Name"
        assert updated.quantity == 5
        mock_repository.save.assert_called_once_with(draft_plan)

    async def test_update_item_on_nonexistent_plan_raises_error(
        self, handler: PlanItemCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None
        command = UpdateItemCommand(plan_id=uuid4(), item_id=uuid4(), equipment_name="X")

        with pytest.raises(EntityNotFoundError):
            await handler.handle_update(command)


class TestRemoveItem:
    async def test_remove_item(
        self, handler: PlanItemCommandHandler, mock_repository: AsyncMock, draft_plan: ProcurementPlan
    ) -> None:
        item = PlanItem(equipment_name="Machine", quantity=1, estimated_unit_price=100.0)
        draft_plan.add_item(item)
        mock_repository.get_by_id.return_value = draft_plan

        command = RemoveItemCommand(plan_id=draft_plan.id, item_id=item.id)
        await handler.handle_remove(command)

        assert len(draft_plan.items) == 0
        mock_repository.save.assert_called_once_with(draft_plan)

    async def test_remove_item_from_nonexistent_plan_raises_error(
        self, handler: PlanItemCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None
        command = RemoveItemCommand(plan_id=uuid4(), item_id=uuid4())

        with pytest.raises(EntityNotFoundError):
            await handler.handle_remove(command)
