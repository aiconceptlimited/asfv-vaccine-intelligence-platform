#!/usr/bin/env python3
"""
PigMatrix adapter.
"""

import subprocess
import shutil
from pathlib import Path
from typing import List
from .base import BaseAdapter
from .result import AdapterResult
from ..canonical_record import CanonicalEpitopeRecord, EpitopeType


class PigMatrixAdapter(BaseAdapter):
    """Adapter for PigMatrix."""
    
    TOOL_NAME = "PigMatrix"
    VERSION = "1.0"
    EXECUTABLE = "pigmatrix"
    
    def __init__(self, alleles: List[str] = None):
        self.alleles = alleles or []
        self._available = None
        self._executable_path = None
    
    def check_available(self) -> bool:
        if self._available is not None:
            return self._available
        self._executable_path = shutil.which(self.EXECUTABLE)
        self._available = self._executable_path is not None
        return self._available
    
    def prepare_input(self, peptides: List[str], output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        input_file = output_dir / "pigmatrix_input.txt"
        with open(input_file, 'w') as f:
            for peptide in peptides:
                f.write(f"{peptide}\n")
        return input_file
    
    def execute(self, input_file: Path, output_dir: Path) -> AdapterResult:
        output_file = output_dir / "pigmatrix.tsv"
        
        if not self.check_available():
            result = AdapterResult(
                tool=self.TOOL_NAME,
                status="TOOL_NOT_AVAILABLE",
                executable_found=False,
                executable_path=self._executable_path,
                raw_output=output_file,
                warnings=[f"Executable '{self.EXECUTABLE}' not found in PATH"]
            )
            with open(output_file, 'w') as f:
                f.write("# TOOL_NOT_AVAILABLE\n")
                f.write(f"# Executable: {self.EXECUTABLE}\n")
                f.write("# peptide\tallele\tscore\trank\n")
            return result
        
        cmd = [
            self.EXECUTABLE,
            "-i", str(input_file),
            "-o", str(output_file)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            result = AdapterResult(
                tool=self.TOOL_NAME,
                status="SUCCESS",
                executable_found=True,
                executable_path=self._executable_path,
                raw_output=output_file,
                warnings=["PigMatrix executed successfully"]
            )
            records = self.parse_output(output_file, "", "")
            result.records = records
            result.record_count = len(records)
            return result
        except subprocess.TimeoutExpired:
            result = AdapterResult(
                tool=self.TOOL_NAME,
                status="TIMEOUT",
                executable_found=True,
                executable_path=self._executable_path,
                raw_output=output_file,
                errors=["PigMatrix execution timed out after 300 seconds"]
            )
            with open(output_file, 'w') as f:
                f.write("# TIMEOUT\n")
                f.write("# peptide\tallele\tscore\trank\n")
            return result
        except subprocess.CalledProcessError as e:
            result = AdapterResult(
                tool=self.TOOL_NAME,
                status="ERROR",
                executable_found=True,
                executable_path=self._executable_path,
                raw_output=output_file,
                errors=[f"PigMatrix failed: {e.stderr[:200]}"]
            )
            with open(output_file, 'w') as f:
                f.write(f"# ERROR: {str(e)}\n")
                f.write("# peptide\tallele\tscore\trank\n")
            return result
    
    def parse_output(self, output_file: Path, protein: str, gene: str) -> List[CanonicalEpitopeRecord]:
        records = []
        if not output_file.exists():
            return records
        with open(output_file, 'r') as f:
            lines = f.readlines()
        data_lines = [l for l in lines if not l.startswith('#') and l.strip()]
        if not data_lines:
            return records
        import csv
        try:
            reader = csv.DictReader(data_lines, delimiter='\t')
            for i, row in enumerate(reader):
                try:
                    peptide = row.get('peptide', '')
                    if not peptide:
                        continue
                    allele = row.get('allele', '')
                    score = float(row.get('score', 0))
                    rank = float(row.get('rank', 100))
                    records.append(CanonicalEpitopeRecord(
                        epitope_id=f"CTL_{gene}_{i+1:06d}" if gene else f"CTL_{i+1:06d}",
                        protein=protein,
                        gene=gene,
                        epitope_type=EpitopeType.CTL,
                        peptide=peptide,
                        start=0,
                        end=len(peptide),
                        length=len(peptide),
                        prediction_tool=self.TOOL_NAME,
                        score=score,
                        rank=rank,
                        conservation=0.0,
                        sla_class_I_allele=allele,
                        binder_class="Weak"
                    ))
                except Exception:
                    continue
        except Exception:
            pass
        return records
    
    def get_tool_name(self) -> str:
        return self.TOOL_NAME
    
    def get_version(self) -> str:
        return self.VERSION
