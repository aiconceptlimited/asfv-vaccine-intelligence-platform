#!/usr/bin/env python3
"""
PipelineContext for Section 3.7 Epitope Discovery pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from .config import DEFAULT_CONFIG
from .constants import PROTEIN_TO_GENE, GENE_TO_PROTEIN


@dataclass
class PipelineContext:
    """Pipeline execution context containing all shared state."""

    # Core identifiers
    protein: str
    gene: str

    # Configuration
    config: Any = field(default_factory=lambda: DEFAULT_CONFIG)

    # Paths
    protein_dir: Optional[Path] = None
    conservation_file: Optional[Path] = None
    output_dir: Optional[Path] = None
    log_dir: Optional[Path] = None

    # Input data
    input_fasta: Optional[Path] = None
    input_fasta_checksum: Optional[str] = None
    conservation_data: Optional[Dict[str, Any]] = None
    conservation_checksum: Optional[str] = None

    # Execution state
    module_name: Optional[str] = None
    module_version: str = "1.0.0"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Output tracking
    outputs: Dict[str, Path] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    completed_modules: List[str] = field(default_factory=list)

    # Logging
    logger: Optional[logging.Logger] = None

    def __post_init__(self):
        """Initialize derived paths."""
        if self.protein and not self.gene:
            self.gene = PROTEIN_TO_GENE.get(self.protein, "")
        if self.gene and not self.protein:
            self.protein = GENE_TO_PROTEIN.get(self.gene, "")

        if self.protein_dir is None:
            self.protein_dir = self.config.protein_dir

        if self.output_dir is None and self.protein:
            self.output_dir = self.config.epitope_dir / self.protein

        if self.log_dir is None:
            self.log_dir = self.config.logs_dir

    def set_input_fasta(self, path: Path) -> None:
        self.input_fasta = path

    def set_conservation_file(self, path: Path) -> None:
        self.conservation_file = path

    def add_output(self, key: str, path: Path) -> None:
        self.outputs[key] = path

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def add_completed_module(self, module: str) -> None:
        if module not in self.completed_modules:
            self.completed_modules.append(module)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protein": self.protein,
            "gene": self.gene,
            "module_name": self.module_name,
            "module_version": self.module_version,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "warnings": self.warnings,
            "errors": self.errors,
            "completed_modules": self.completed_modules
        }
