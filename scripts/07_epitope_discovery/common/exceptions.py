#!/usr/bin/env python3
"""
Custom exceptions for Section 3.7 Epitope Discovery pipeline.
"""

class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass

class ProteinFileMissingError(PipelineError):
    pass

class ConservationFileMissingError(PipelineError):
    pass

class InvalidFastaError(PipelineError):
    pass

class ConservationMismatchError(PipelineError):
    pass

class DuplicateIdentifierError(PipelineError):
    pass

class InvalidAminoAcidError(PipelineError):
    pass

class StopCodonError(PipelineError):
    pass

class ManifestError(PipelineError):
    pass

class QCFailure(PipelineError):
    pass

class ParsingError(PipelineError):
    pass

class ConfigError(PipelineError):
    pass

class ValidationError(PipelineError):
    pass

class ChecksumMismatchError(PipelineError):
    pass
