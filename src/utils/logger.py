"""Logger setup for Kallisto-OSINTer."""

import logging
import os
from typing import Optional


def _env_to_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_level(level: Optional[int]) -> int:
    if level is not None:
        return level

    env_level = os.getenv("KALLISTO_LOG_LEVEL")
    if env_level:
        return getattr(logging, env_level.upper(), logging.INFO)

    if _env_to_bool(os.getenv("KALLISTO_DEBUG")):
        return logging.DEBUG

    return logging.INFO


def get_logger(name: str, log_file: Optional[str] = None, level: Optional[int] = None) -> logging.Logger:
    """Configure and return a logger."""

    logger = logging.getLogger(name)

    resolved_level = _resolve_level(level)
    logger.setLevel(resolved_level)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(resolved_level)
        logger.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(resolved_level)
            logger.addHandler(file_handler)

    return logger
