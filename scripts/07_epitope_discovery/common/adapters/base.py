#!/usr/bin/env python3
"""
Base adapter for prediction tools.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..canonical_record import CanonicalEpitopeRecord


class BaseAdapter(ABC):
    """Base class for all prediction tool adapters."""
    
    @abstractmethod
    def prepare_input(self, peptides: List[str], output_dir: Path) -> Path:
        """Prepare input file for the tool."""
        pass
    
    @abstractmethod
    def execute(self, input_file: Path, output_dir: Path) -> Path:
        """Execute the prediction tool."""
        pass
    
    @abstractmethod
    def parse_output(self, output_file: Path, protein: str, gene: str) -> List[CanonicalEpitopeRecord]:
        """Parse native output to Canonical Epitope Records."""
        pass
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """Return tool name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return tool version."""
        pass
    
    @abstractmethod
    def check_available(self) -> bool:
        """Check if the tool is available."""
        pass
