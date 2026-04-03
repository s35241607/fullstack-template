from dataclasses import dataclass
from uuid import UUID

from app.domain.order.entities.purchase_order import PurchaseOrder
from app.domain.order.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.order.value_objects.order_status import OrderStatus
from app.domain.shared.exceptions import EntityNotFoundError


@dataclass
class GetOrderQuery:
    order_id: UUID


@dataclass
class ListOrdersQuery:
    status: str | None = None


@dataclass
class GetHoldsByModelQuery:
    model_name: str


@dataclass
class ListModelHoldSummaryQuery:
    pass


class OrderQueryHandler:
    """訂單查詢 handler。"""

    def __init__(self, repository: PurchaseOrderRepository) -> None:
        self._repository = repository

    async def handle_get(self, query: GetOrderQuery) -> PurchaseOrder:
        order = await self._repository.get_by_id(query.order_id)
        if order is None:
            raise EntityNotFoundError("PurchaseOrder", query.order_id)
        return order

    async def handle_list(self, query: ListOrdersQuery) -> list[PurchaseOrder]:
        status = OrderStatus(query.status) if query.status else None
        return await self._repository.get_all(status=status)

    async def handle_holds_by_model(self, query: GetHoldsByModelQuery) -> list[dict[str, object]]:
        return await self._repository.get_holds_by_model(query.model_name)

    async def handle_model_hold_summary(self, query: ListModelHoldSummaryQuery) -> list[dict[str, object]]:  # noqa: ARG002
        return await self._repository.get_all_model_hold_summary()
