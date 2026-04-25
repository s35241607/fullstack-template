import logging
import json
import sys
import time
from datetime import datetime
from typing import Any

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON records.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }
        
        # Include extra fields if they exist
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)


def setup_logging() -> None:
    """
    Sets up the logging configuration for the application.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.JSON_LOGS:
        console_handler.setFormatter(JSONFormatter())
    else:
        # standard format for local development
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_handler.setFormatter(logging.Formatter(fmt))
        
    root_logger.addHandler(console_handler)
    
    # Silent noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
