#!/usr/bin/env python3
"""
Version compatibility for Section 3.7 Epitope Discovery pipeline.
"""

from .config import PIPELINE_VERSION
from .exceptions import ConfigError


def check_version(required_version: str) -> bool:
    """
    Check if the pipeline version meets the requirement.

    Raises:
        ConfigError: If versions are incompatible
    """
    if required_version != PIPELINE_VERSION:
        raise ConfigError(
            f"Incompatible pipeline version: required {required_version}, "
            f"current {PIPELINE_VERSION}"
        )
    return True
