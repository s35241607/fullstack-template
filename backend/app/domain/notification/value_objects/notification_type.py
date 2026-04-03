from enum import Enum


class NotificationType(str, Enum):
    """通知類型。"""

    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
