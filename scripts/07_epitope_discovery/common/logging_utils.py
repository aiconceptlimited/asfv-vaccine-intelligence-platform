#!/usr/bin/env python3
"""
Standardized logging for Section 3.7 Epitope Discovery pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    module_name: str,
    protein: str,
    log_dir: Optional[Path] = None,
    log_level: int = logging.INFO,
    console_output: bool = True
) -> logging.Logger:
    """Set up logging with consistent format."""
    logger = logging.getLogger(f"{module_name}.{protein}")
    logger.setLevel(log_level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{protein}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
