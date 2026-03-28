from enum import Enum


class PlanStatus(str, Enum):
    """採購計畫狀態。"""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
