#!/usr/bin/env python3
"""
Enums for Section 3.7 Epitope Discovery pipeline.
"""

from enum import Enum


class QCStatus(Enum):
    """Quality control status."""
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    PENDING = "PENDING"


class EpitopeType(Enum):
    """Epitope type."""
    CTL = "CTL"
    HTL = "HTL"
    BCELL = "B-cell"


class SLAClass(Enum):
    """SLA class."""
    CLASS_I = "I"
    CLASS_II = "II"


class BinderClass(Enum):
    """Binder class."""
    STRONG = "Strong"
    WEAK = "Weak"
    NON_BINDER = "Non-binder"


class ExitCode(Enum):
    """Standard exit codes."""
    SUCCESS = 0
    VALIDATION_FAILURE = 1
    MISSING_INPUT = 2
    PARSING_ERROR = 3
    CONFIG_ERROR = 4
    INTERNAL_EXCEPTION = 5


class ToolName(Enum):
    """Prediction tool names."""
    NETMHCPAN = "NetMHCpan-4.1"
    PIGMATRIX = "PigMatrix"
    NETMHCIIPAN = "NetMHCIIpan"
    BEPIPRED = "BepiPred-3.0"
    DEEPLBCEPRED = "DeepLBCEPred"
