#!/usr/bin/env python3
"""
Standardized file I/O operations.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

from .exceptions import InvalidFastaError


def read_fasta(path: Union[str, Path]) -> List[SeqRecord]:
    """Read a FASTA file and return SeqRecord objects."""
    path = Path(path)
    if not path.exists():
        raise InvalidFastaError(f"FASTA file not found: {path}")

    try:
        records = list(SeqIO.parse(path, "fasta"))
        if not records:
            raise InvalidFastaError(f"FASTA file contains no records: {path}")
        return records
    except Exception as e:
        raise InvalidFastaError(f"Failed to parse FASTA file {path}: {e}")


def write_fasta(path: Union[str, Path], records: List[SeqRecord]) -> None:
    """Write SeqRecord objects to a FASTA file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    SeqIO.write(records, path, "fasta")


def read_json(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a JSON file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, 'r') as f:
        return json.load(f)


def write_json(path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> None:
    """Write data to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)


def read_tsv(path: Union[str, Path]) -> List[Dict[str, str]]:
    """Read a TSV file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"TSV file not found: {path}")
    with open(path, 'r') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def write_tsv(path: Union[str, Path], data: List[Dict[str, Any]]) -> None:
    """Write a list of dictionaries to a TSV file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not data:
        raise ValueError("No data to write")
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()), delimiter='\t')
        writer.writeheader()
        writer.writerows(data)


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_exists(path: Union[str, Path]) -> bool:
    """Check if a file exists."""
    return Path(path).exists()


def get_file_size(path: Union[str, Path]) -> int:
    """Get file size in bytes."""
    return Path(path).stat().st_size
