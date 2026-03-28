from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.example.handlers.item_command_handler import (
    CreateItemCommand,
    DeleteItemCommand,
    ItemCommandHandler,
    UpdateItemCommand,
)
from app.application.example.handlers.item_query_handler import (
    GetItemQuery,
    ItemQueryHandler,
    ListItemsQuery,
)
from app.domain.shared.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.infrastructure.database.repositories.sqlalchemy_item_repository import (
    SqlAlchemyItemRepository,
)
from app.infrastructure.database.session import get_db_session
from app.interfaces.api.v1.schemas.item_schema import (
    ItemCreateRequest,
    ItemResponse,
    ItemUpdateRequest,
)

router = APIRouter(prefix="/items", tags=["items"])


def get_item_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> ItemCommandHandler:
    return ItemCommandHandler(SqlAlchemyItemRepository(session))


def get_item_query_handler(
    session: AsyncSession = Depends(get_db_session),
) -> ItemQueryHandler:
    return ItemQueryHandler(SqlAlchemyItemRepository(session))


@router.get("/", response_model=list[ItemResponse])
async def list_items(
    handler: ItemQueryHandler = Depends(get_item_query_handler),
) -> list[ItemResponse]:
    items = await handler.handle_list(ListItemsQuery())
    return [
        ItemResponse(id=item.id, name=item.name, description=item.description)
        for item in items
    ]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID,
    handler: ItemQueryHandler = Depends(get_item_query_handler),
) -> ItemResponse:
    try:
        item = await handler.handle_get(GetItemQuery(item_id=item_id))
        return ItemResponse(id=item.id, name=item.name, description=item.description)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: ItemCreateRequest,
    handler: ItemCommandHandler = Depends(get_item_command_handler),
) -> ItemResponse:
    try:
        item = await handler.handle_create(
            CreateItemCommand(name=body.name, description=body.description)
        )
        return ItemResponse(id=item.id, name=item.name, description=item.description)
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    body: ItemUpdateRequest,
    handler: ItemCommandHandler = Depends(get_item_command_handler),
) -> ItemResponse:
    try:
        item = await handler.handle_update(
            UpdateItemCommand(
                item_id=item_id, name=body.name, description=body.description
            )
        )
        return ItemResponse(id=item.id, name=item.name, description=item.description)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    handler: ItemCommandHandler = Depends(get_item_command_handler),
) -> None:
    try:
        await handler.handle_delete(DeleteItemCommand(item_id=item_id))
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
