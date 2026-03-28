from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.procurement.handlers.plan_command_handler import (
    CreatePlanCommand,
    DeletePlanCommand,
    ProcurementPlanCommandHandler,
    SubmitPlanCommand,
    UpdatePlanCommand,
)
from app.domain.procurement.entities.plan_item import PlanItem
from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.procurement.value_objects.plan_status import PlanStatus
from app.domain.shared.exceptions import EntityNotFoundError


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_repository: AsyncMock) -> ProcurementPlanCommandHandler:
    return ProcurementPlanCommandHandler(mock_repository)


class TestCreatePlan:
    async def test_create_plan(self, handler: ProcurementPlanCommandHandler, mock_repository: AsyncMock) -> None:
        command = CreatePlanCommand(name="Q3 Plan", planned_date=date(2025, 7, 1))
        plan = await handler.handle_create(command)

        assert plan.name == "Q3 Plan"
        assert plan.planned_date == date(2025, 7, 1)
        assert plan.status == PlanStatus.DRAFT
        mock_repository.save.assert_called_once_with(plan)


class TestUpdatePlan:
    async def test_update_plan(self, handler: ProcurementPlanCommandHandler, mock_repository: AsyncMock) -> None:
        existing = ProcurementPlan(name="Old Name", planned_date=date(2025, 1, 1))
        mock_repository.get_by_id.return_value = existing

        command = UpdatePlanCommand(plan_id=existing.id, name="New Name")
        plan = await handler.handle_update(command)

        assert plan.name == "New Name"
        mock_repository.save.assert_called_once_with(existing)

    async def test_update_nonexistent_plan_raises_error(
        self, handler: ProcurementPlanCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None
        command = UpdatePlanCommand(plan_id=uuid4(), name="Name")

        with pytest.raises(EntityNotFoundError):
            await handler.handle_update(command)


class TestDeletePlan:
    async def test_delete_plan(self, handler: ProcurementPlanCommandHandler, mock_repository: AsyncMock) -> None:
        existing = ProcurementPlan(name="To Delete", planned_date=date(2025, 1, 1))
        mock_repository.get_by_id.return_value = existing

        command = DeletePlanCommand(plan_id=existing.id)
        await handler.handle_delete(command)

        mock_repository.delete.assert_called_once_with(existing.id)

    async def test_delete_nonexistent_plan_raises_error(
        self, handler: ProcurementPlanCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError):
            await handler.handle_delete(DeletePlanCommand(plan_id=uuid4()))


class TestSubmitPlan:
    async def test_submit_plan(self, handler: ProcurementPlanCommandHandler, mock_repository: AsyncMock) -> None:
        existing = ProcurementPlan(name="Plan", planned_date=date(2025, 1, 1))
        existing.add_item(PlanItem(equipment_name="Machine A", quantity=1, estimated_unit_price=100.0))
        mock_repository.get_by_id.return_value = existing

        command = SubmitPlanCommand(plan_id=existing.id)
        plan = await handler.handle_submit(command)

        assert plan.status == PlanStatus.SUBMITTED
        mock_repository.save.assert_called_once_with(existing)

    async def test_submit_nonexistent_plan_raises_error(
        self, handler: ProcurementPlanCommandHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError):
            await handler.handle_submit(SubmitPlanCommand(plan_id=uuid4()))
