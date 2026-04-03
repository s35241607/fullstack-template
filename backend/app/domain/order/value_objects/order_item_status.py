from enum import Enum


class OrderItemStatus(str, Enum):
    """訂單項目狀態。"""

    PENDING = "PENDING"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    FULLY_RECEIVED = "FULLY_RECEIVED"
