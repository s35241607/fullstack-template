from enum import Enum


class HoldStatus(str, Enum):
    """On-Hold 狀態。"""

    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
