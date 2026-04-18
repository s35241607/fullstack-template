from enum import StrEnum


class NotificationType(StrEnum):
    """通知類型。"""

    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
