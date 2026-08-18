#!/usr/bin/env python3
"""
Centralized configuration for Section 3.7 Epitope Discovery pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable pipeline configuration."""
    pipeline_version: str = "2.0"
    data_root: Path = Path("data")
    protein_dir: Path = Path("data/interim/proteins")
    conservation_dir: Path = Path("data/processed/conservation")
    epitope_dir: Path = Path("data/processed/epitopes")
    sla_panel_dir: Path = Path("data/processed/sla/reference_panel_final")
    raw_sla_dir: Path = Path("data/raw/sla/ipd_release")
    logs_dir: Path = Path("logs/07_epitope_discovery")
    results_dir: Path = Path("results/07_epitopes")
    config_dir: Path = Path("config")
    reference_dir: Path = Path("data/reference")
    fasta_ext: str = ".fasta"
    json_ext: str = ".json"
    tsv_ext: str = ".tsv"
    log_ext: str = ".log"


DEFAULT_CONFIG = PipelineConfig()
PIPELINE_VERSION = DEFAULT_CONFIG.pipeline_version
