from enum import Enum


class PlanStatus(str, Enum):
    """採購計畫狀態。"""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    EE_REVIEW = "EE_REVIEW"
    QUOTED = "QUOTED"
    APPROVED = "APPROVED"
    BUDGET_SUBMITTED = "BUDGET_SUBMITTED"


class PlanItemStatus(str, Enum):
    """採購計畫項目狀態。"""

    PENDING = "PENDING"
    SPEC_UPLOADED = "SPEC_UPLOADED"
    QUOTED = "QUOTED"
    APPROVED = "APPROVED"
