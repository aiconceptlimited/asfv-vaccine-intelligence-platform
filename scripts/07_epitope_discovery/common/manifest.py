#!/usr/bin/env python3
"""
Manifest file interface for Section 3.7 Epitope Discovery pipeline.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from .config import DEFAULT_CONFIG
from .io import read_json, write_json
from .exceptions import ManifestError


def create_manifest(
    protein: str,
    gene: str,
    input_fasta: str,
    input_fasta_checksum: str,
    conservation_file: str,
    conservation_checksum: str,
    outputs: Dict[str, str],
    module: str,
    qc_status: str = "PENDING",
    next_module: Optional[str] = None
) -> Dict[str, Any]:
    """Create a manifest for a protein."""
    return {
        "protein": protein,
        "gene": gene,
        "input_fasta": input_fasta,
        "input_fasta_checksum": input_fasta_checksum,
        "conservation_file": conservation_file,
        "conservation_checksum": conservation_checksum,
        "outputs": outputs,
        "modules_completed": [],
        "current_module": module,
        "pipeline_version": DEFAULT_CONFIG.pipeline_version,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "qc_status": qc_status,
        "next_module": next_module
    }


def update_manifest(
    path: Path,
    module: str,
    outputs: Optional[Dict[str, str]] = None,
    qc_status: Optional[str] = None,
    next_module: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing manifest."""
    try:
        manifest = read_json(path)
    except FileNotFoundError:
        raise ManifestError(f"Manifest file not found: {path}")

    if module not in manifest.get("modules_completed", []):
        manifest.setdefault("modules_completed", []).append(module)

    manifest["current_module"] = module
    manifest["last_updated"] = datetime.now().isoformat()

    if outputs:
        manifest["outputs"].update(outputs)
    if qc_status:
        manifest["qc_status"] = qc_status
    if next_module:
        manifest["next_module"] = next_module

    write_json(path, manifest)
    return manifest


def read_manifest(path: Path) -> Dict[str, Any]:
    """Read and return the manifest."""
    try:
        return read_json(path)
    except FileNotFoundError:
        raise ManifestError(f"Manifest file not found: {path}")


def get_completed_modules(path: Path) -> List[str]:
    """Get the list of completed modules."""
    return read_manifest(path).get("modules_completed", [])
