from abc import abstractmethod

from app.domain.order.entities.purchase_order import PurchaseOrder
from app.domain.order.value_objects.order_status import OrderStatus
from app.domain.shared.repository import Repository


class PurchaseOrderRepository(Repository[PurchaseOrder]):
    """採購訂單倉儲介面。"""

    @abstractmethod
    async def get_all(self, status: OrderStatus | None = None) -> list[PurchaseOrder]: ...

    @abstractmethod
    async def get_by_order_number(self, order_number: str) -> PurchaseOrder | None: ...

    @abstractmethod
    async def get_holds_by_model(self, model_name: str) -> list[dict[str, object]]: ...

    @abstractmethod
    async def get_all_model_hold_summary(self) -> list[dict[str, object]]: ...
