from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.database.models.procurement_plan_model import PlanItemModel, ProcurementPlanModel
from app.infrastructure.database.session import get_db_session
from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        # Only create procurement-related tables to avoid JSONB issues with SQLite
        await conn.run_sync(ProcurementPlanModel.__table__.create)
        await conn.run_sync(PlanItemModel.__table__.create)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(PlanItemModel.__table__.drop)
        await conn.run_sync(ProcurementPlanModel.__table__.drop)
    await engine.dispose()


class TestProcurementPlanRouter:
    async def test_list_plans_returns_empty_list(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/procurement-plans/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_plan(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Q3 Equipment Plan", "planned_date": "2025-07-01"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Q3 Equipment Plan"
        assert data["planned_date"] == "2025-07-01"
        assert data["status"] == "DRAFT"
        assert data["total_amount"] == 0.0
        assert data["items"] == []
        assert "id" in data

    async def test_get_nonexistent_plan_returns_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/procurement-plans/{uuid4()}")
        assert response.status_code == 404

    async def test_create_and_get_plan(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "My Plan", "planned_date": "2025-06-01"},
        )
        plan_id = create_resp.json()["id"]

        get_resp = await client.get(f"/api/v1/procurement-plans/{plan_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == plan_id

    async def test_update_plan(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Old Name", "planned_date": "2025-01-01"},
        )
        plan_id = create_resp.json()["id"]

        update_resp = await client.patch(
            f"/api/v1/procurement-plans/{plan_id}",
            json={"name": "New Name"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "New Name"

    async def test_delete_plan(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "To Delete", "planned_date": "2025-01-01"},
        )
        plan_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/api/v1/procurement-plans/{plan_id}")
        assert delete_resp.status_code == 204

        get_resp = await client.get(f"/api/v1/procurement-plans/{plan_id}")
        assert get_resp.status_code == 404

    async def test_add_item_to_plan(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Plan", "planned_date": "2025-06-01"},
        )
        plan_id = create_resp.json()["id"]

        item_resp = await client.post(
            f"/api/v1/procurement-plans/{plan_id}/items",
            json={
                "equipment_name": "CNC Machine",
                "specification": "5-axis",
                "quantity": 2,
                "estimated_unit_price": 50000.0,
            },
        )
        assert item_resp.status_code == 201
        data = item_resp.json()
        assert data["equipment_name"] == "CNC Machine"
        assert data["quantity"] == 2

    async def test_submit_plan_with_items(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Plan", "planned_date": "2025-06-01"},
        )
        plan_id = create_resp.json()["id"]

        await client.post(
            f"/api/v1/procurement-plans/{plan_id}/items",
            json={"equipment_name": "Drill", "quantity": 1, "estimated_unit_price": 1000.0},
        )

        submit_resp = await client.post(f"/api/v1/procurement-plans/{plan_id}/submit")
        assert submit_resp.status_code == 200
        assert submit_resp.json()["status"] == "SUBMITTED"

    async def test_submit_plan_without_items_returns_422(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Empty Plan", "planned_date": "2025-06-01"},
        )
        plan_id = create_resp.json()["id"]

        submit_resp = await client.post(f"/api/v1/procurement-plans/{plan_id}/submit")
        assert submit_resp.status_code == 422

    async def test_update_item(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Plan", "planned_date": "2025-06-01"},
        )
        plan_id = create_resp.json()["id"]

        item_resp = await client.post(
            f"/api/v1/procurement-plans/{plan_id}/items",
            json={"equipment_name": "Old Name", "quantity": 1, "estimated_unit_price": 100.0},
        )
        item_id = item_resp.json()["id"]

        update_resp = await client.patch(
            f"/api/v1/procurement-plans/{plan_id}/items/{item_id}",
            json={"equipment_name": "New Name", "quantity": 5},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["equipment_name"] == "New Name"
        assert update_resp.json()["quantity"] == 5

    async def test_remove_item(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Plan", "planned_date": "2025-06-01"},
        )
        plan_id = create_resp.json()["id"]

        item_resp = await client.post(
            f"/api/v1/procurement-plans/{plan_id}/items",
            json={"equipment_name": "Machine", "quantity": 1, "estimated_unit_price": 100.0},
        )
        item_id = item_resp.json()["id"]

        delete_resp = await client.delete(f"/api/v1/procurement-plans/{plan_id}/items/{item_id}")
        assert delete_resp.status_code == 204

    async def test_total_amount_calculation(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/procurement-plans/",
            json={"name": "Plan", "planned_date": "2025-06-01"},
        )
        plan_id = create_resp.json()["id"]

        await client.post(
            f"/api/v1/procurement-plans/{plan_id}/items",
            json={"equipment_name": "A", "quantity": 2, "estimated_unit_price": 100.0},
        )
        await client.post(
            f"/api/v1/procurement-plans/{plan_id}/items",
            json={"equipment_name": "B", "quantity": 3, "estimated_unit_price": 200.0},
        )

        get_resp = await client.get(f"/api/v1/procurement-plans/{plan_id}")
        assert get_resp.json()["total_amount"] == 800.0
