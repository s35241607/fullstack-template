from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["example"])


@router.get("/")
async def list_items() -> list[dict[str, Any]]:
    return [{"id": 1, "name": "Item One"}, {"id": 2, "name": "Item Two"}]


@router.get("/{item_id}")
async def get_item(item_id: int) -> dict[str, Any]:
    return {"id": item_id, "name": f"Item {item_id}"}
