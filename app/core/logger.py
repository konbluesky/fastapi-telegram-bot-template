"""Logger initialization using loguru, intercepts all standard logging."""

import logging
import sys

from loguru import logger as _logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        _logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage())


def init_logger() -> None:
    """Initialize loguru logger and intercept all standard logging."""
    _logger.remove()

    # Console handler
    _logger.add(sys.stderr, format=settings.log.format, level=settings.log.level,
                colorize=True, backtrace=True, diagnose=settings.debug)

    # File handler for production
    if not settings.debug:
        _logger.add("logs/app.log", format=settings.log.format, level=settings.log.level, rotation=settings.log.rotation,
                    retention=settings.log.retention, compression="zip", backtrace=True, diagnose=False)

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Configure third-party loggers
    loggers_config = {
        "uvicorn": settings.log.level, "uvicorn.error": settings.log.level, "uvicorn.access": settings.log.level,
        "fastapi": settings.log.level,
        "sqlalchemy": "WARNING", "sqlalchemy.engine": "WARNING" if not settings.database.echo else "INFO",
        "aiogram": settings.log.level, "aiogram.event": settings.log.level, "aiogram.dispatcher": settings.log.level,
        "apscheduler": settings.log.level,
        "asyncio": "WARNING", "redis": "WARNING",
    }
    for logger_name, level in loggers_config.items():
        logging_logger = logging.getLogger(logger_name)
        logging_logger.setLevel(level)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    _logger.info(
        "Logger initialized with loguru, intercepting all standard logging")


# Export logger for use across the application
logger = _logger
