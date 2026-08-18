#!/usr/bin/env python3
"""
Common library for Section 3.7 Epitope Discovery pipeline.
"""

from .config import DEFAULT_CONFIG, PipelineConfig, PIPELINE_VERSION
from .constants import (
    VALID_AMINO_ACIDS, AMBIGUOUS_AMINO_ACIDS, SUPPORTED_PROTEINS,
    GENE_TO_PROTEIN, PROTEIN_TO_GENE, PROTEIN_PROCESSING_ORDER
)
from .enums import (
    QCStatus, EpitopeType, SLAClass, BinderClass, ExitCode, ToolName
)
from .exceptions import (
    PipelineError, ProteinFileMissingError, ConservationFileMissingError,
    InvalidFastaError, ConservationMismatchError, DuplicateIdentifierError,
    InvalidAminoAcidError, StopCodonError, ManifestError, QCFailure,
    ParsingError, ConfigError, ValidationError, ChecksumMismatchError
)
from .io import (
    read_fasta, write_fasta, read_json, write_json,
    read_tsv, write_tsv, ensure_directory, file_exists, get_file_size
)
from .checksums import (
    generate_checksum, verify_checksum, generate_checksum_from_string
)
from .logging_utils import setup_logging
from .schemas import (
    SEQUENCE_QC_SCHEMA, PREDICTION_QC_SCHEMA, PROTEIN_SUMMARY_SCHEMA,
    MANIFEST_SCHEMA, PROVENANCE_SCHEMA, validate_against_schema, validate_json_file
)
from .validation import (
    validate_fasta, validate_sequence, validate_peptide,
    validate_conservation, validate_linkage,
    validate_coordinates, validate_canonical_record
)
from .manifest import create_manifest, update_manifest, read_manifest, get_completed_modules
from .provenance import generate_provenance
from .canonical_record import CanonicalEpitopeRecord
from .context import PipelineContext
from .version import check_version
from .adapters import AdapterRegistry, BaseAdapter

__version__ = "1.0.0"

__all__ = [
    "DEFAULT_CONFIG", "PipelineConfig", "PIPELINE_VERSION",
    "VALID_AMINO_ACIDS", "AMBIGUOUS_AMINO_ACIDS", "SUPPORTED_PROTEINS",
    "GENE_TO_PROTEIN", "PROTEIN_TO_GENE", "PROTEIN_PROCESSING_ORDER",
    "QCStatus", "EpitopeType", "SLAClass", "BinderClass", "ExitCode", "ToolName",
    "PipelineError", "ProteinFileMissingError", "ConservationFileMissingError",
    "InvalidFastaError", "ConservationMismatchError", "DuplicateIdentifierError",
    "InvalidAminoAcidError", "StopCodonError", "ManifestError", "QCFailure",
    "ParsingError", "ConfigError", "ValidationError", "ChecksumMismatchError",
    "read_fasta", "write_fasta", "read_json", "write_json",
    "read_tsv", "write_tsv", "ensure_directory", "file_exists", "get_file_size",
    "generate_checksum", "verify_checksum", "generate_checksum_from_string",
    "setup_logging",
    "SEQUENCE_QC_SCHEMA", "PREDICTION_QC_SCHEMA", "PROTEIN_SUMMARY_SCHEMA",
    "MANIFEST_SCHEMA", "PROVENANCE_SCHEMA", "validate_against_schema", "validate_json_file",
    "validate_fasta", "validate_sequence", "validate_peptide",
    "validate_conservation", "validate_linkage",
    "validate_coordinates", "validate_canonical_record",
    "create_manifest", "update_manifest", "read_manifest", "get_completed_modules",
    "generate_provenance",
    "CanonicalEpitopeRecord",
    "PipelineContext",
    "check_version",
    "AdapterRegistry", "BaseAdapter"
]
