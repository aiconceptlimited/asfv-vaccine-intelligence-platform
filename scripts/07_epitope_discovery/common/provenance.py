#!/usr/bin/env python3
"""
Provenance generation for Section 3.7 Epitope Discovery pipeline.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import platform
import sys
from .config import DEFAULT_CONFIG


def generate_provenance(
    module: str,
    protein: str,
    gene: str,
    software_versions: Dict[str, str],
    checksums: Dict[str, str],
    status: str = "PASS",
    duration: Optional[float] = None
) -> Dict[str, Any]:
    """Generate a complete provenance record."""
    provenance = {
        "pipeline_version": DEFAULT_CONFIG.pipeline_version,
        "module": module,
        "protein": protein,
        "gene": gene,
        "software": software_versions,
        "checksums": checksums,
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "hostname": platform.node()
        },
        "execution_timestamp": datetime.now().isoformat(),
        "status": status
    }

    if duration is not None:
        provenance["execution_duration_seconds"] = round(duration, 2)

    return provenance
