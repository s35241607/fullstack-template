from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.procurement.handlers.plan_query_handler import (
    GetPlanQuery,
    ListPlansQuery,
    ProcurementPlanQueryHandler,
)
from app.domain.procurement.entities.procurement_plan import ProcurementPlan
from app.domain.shared.exceptions import EntityNotFoundError


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_repository: AsyncMock) -> ProcurementPlanQueryHandler:
    return ProcurementPlanQueryHandler(mock_repository)


class TestGetPlan:
    async def test_get_existing_plan(self, handler: ProcurementPlanQueryHandler, mock_repository: AsyncMock) -> None:
        plan = ProcurementPlan(name="Plan", planned_date=date(2025, 6, 1))
        mock_repository.get_by_id.return_value = plan

        result = await handler.handle_get(GetPlanQuery(plan_id=plan.id))

        assert result == plan
        mock_repository.get_by_id.assert_called_once_with(plan.id)

    async def test_get_nonexistent_plan_raises_error(
        self, handler: ProcurementPlanQueryHandler, mock_repository: AsyncMock
    ) -> None:
        mock_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError):
            await handler.handle_get(GetPlanQuery(plan_id=uuid4()))


class TestListPlans:
    async def test_list_plans(self, handler: ProcurementPlanQueryHandler, mock_repository: AsyncMock) -> None:
        plans = [
            ProcurementPlan(name="Plan A", planned_date=date(2025, 1, 1)),
            ProcurementPlan(name="Plan B", planned_date=date(2025, 2, 1)),
        ]
        mock_repository.get_all.return_value = plans

        result = await handler.handle_list(ListPlansQuery())

        assert len(result) == 2
        mock_repository.get_all.assert_called_once()

    async def test_list_empty(self, handler: ProcurementPlanQueryHandler, mock_repository: AsyncMock) -> None:
        mock_repository.get_all.return_value = []

        result = await handler.handle_list(ListPlansQuery())

        assert result == []
