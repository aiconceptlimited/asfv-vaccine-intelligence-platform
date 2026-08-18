#!/usr/bin/env python3
"""
Tool adapters for Section 3.7 Epitope Discovery pipeline.
"""

from .base import BaseAdapter
from .registry import AdapterRegistry
from .result import AdapterResult
from .netmhcpan import NetMHCpanAdapter
from .pigmatrix import PigMatrixAdapter
from ..enums import ToolName

# Register adapters
AdapterRegistry.register(ToolName.NETMHCPAN, NetMHCpanAdapter)
AdapterRegistry.register(ToolName.PIGMATRIX, PigMatrixAdapter)

__all__ = [
    "BaseAdapter",
    "AdapterRegistry",
    "AdapterResult",
    "NetMHCpanAdapter",
    "PigMatrixAdapter",
]
