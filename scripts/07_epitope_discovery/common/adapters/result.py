#!/usr/bin/env python3
"""
Adapter result structure.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from ..canonical_record import CanonicalEpitopeRecord


@dataclass
class AdapterResult:
    """Result from a prediction tool adapter."""
    
    tool: str
    status: str  # "SUCCESS", "TOOL_NOT_AVAILABLE", "ERROR", "TIMEOUT"
    executable_found: bool
    raw_output: Optional[Path] = None
    records: List[CanonicalEpitopeRecord] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    record_count: int = 0
    executable_path: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "tool": self.tool,
            "status": self.status,
            "executable_found": self.executable_found,
            "raw_output": str(self.raw_output) if self.raw_output else None,
            "record_count": len(self.records),
            "warnings": self.warnings,
            "errors": self.errors,
            "executable_path": self.executable_path
        }
    
    def has_records(self) -> bool:
        """Return True if any records were parsed."""
        return len(self.records) > 0
