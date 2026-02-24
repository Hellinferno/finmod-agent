"""
Logging configuration for the FMVA system.

Uses Loguru for structured, colored console output and persistent file logs.
Every module should import `logger` from this module.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from fmva.config import LOG_DIR


def configure_logging(
    session_name: Optional[str] = None,
    log_dir: Optional[str] = None,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
) -> "logger":
    """
    Configure Loguru for FMVA.

    Args:
        session_name: Optional session identifier. Auto-generated if None.
        log_dir: Directory for log files. Defaults to project LOG_DIR.
        console_level: Minimum log level for console output.
        file_level: Minimum log level for file output.

    Returns:
        Configured logger instance.
    """
    logger.remove()  # Remove default handler

    # Session name
    if not session_name:
        session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Log directory
    log_path = Path(log_dir) if log_dir else LOG_DIR
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / f"{session_name}.log"

    # Console output (colored)
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=console_level,
        colorize=True,
    )

    # File output (full detail)
    logger.add(
        str(log_file),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        level=file_level,
        rotation="50 MB",
        retention="7 days",
        compression="zip",
    )

    logger.info(f"Logging initialized → {log_file}")
    return logger


def get_logger(name: str) -> "logger":
    """Get a contextualized logger for a specific module."""
    return logger.bind(module=name)
