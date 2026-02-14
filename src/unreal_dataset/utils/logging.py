"""Unified logging configuration for Unreal Dataset."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for the Unreal Dataset package.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        format_string: Optional custom format string

    Returns:
        Configured root logger for the package
    """
    if format_string is None:
        format_string = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    # Get the package logger
    logger = logging.getLogger("unreal_dataset")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (e.g., "unreal_dataset.client")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class UnrealLogAdapter:
    """
    Adapter that wraps Python logging for use in Unreal Engine context.

    When running inside Unreal, this redirects logging calls to unreal.log().
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._unreal = None

    def _get_unreal(self):
        """Lazy import of unreal module."""
        if self._unreal is None:
            try:
                import unreal
                self._unreal = unreal
            except ImportError:
                self._unreal = False
        return self._unreal

    def debug(self, msg: str) -> None:
        """Log debug message."""
        unreal = self._get_unreal()
        if unreal:
            unreal.log(f"[DEBUG] {msg}")
        else:
            self.logger.debug(msg)

    def info(self, msg: str) -> None:
        """Log info message."""
        unreal = self._get_unreal()
        if unreal:
            unreal.log(msg)
        else:
            self.logger.info(msg)

    def warning(self, msg: str) -> None:
        """Log warning message."""
        unreal = self._get_unreal()
        if unreal:
            unreal.log_warning(msg)
        else:
            self.logger.warning(msg)

    def error(self, msg: str) -> None:
        """Log error message."""
        unreal = self._get_unreal()
        if unreal:
            unreal.log_error(msg)
        else:
            self.logger.error(msg)
