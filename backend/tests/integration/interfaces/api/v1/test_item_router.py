import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


class TestItemRouter:
    async def test_list_items_returns_empty_list(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/items/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_item(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/items/",
            json={"name": "Test Item", "description": "A test"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["description"] == "A test"
        assert "id" in data

    async def test_get_nonexistent_item_returns_404(self, client: AsyncClient) -> None:
        from uuid import uuid4
        response = await client.get(f"/api/v1/items/{uuid4()}")
        assert response.status_code == 404

    async def test_create_and_get_item(self, client: AsyncClient) -> None:
        create_response = await client.post(
            "/api/v1/items/",
            json={"name": "My Item"},
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["id"]

        get_response = await client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == item_id
