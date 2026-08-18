#!/usr/bin/env python3
"""
SHA-256 checksum generation and verification.
"""

import hashlib
from pathlib import Path
from typing import Union


def generate_checksum(file_path: Union[str, Path]) -> str:
    """Generate SHA-256 checksum for a file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def generate_checksum_from_string(data: str) -> str:
    """Generate SHA-256 checksum from a string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def verify_checksum(file_path: Union[str, Path], expected: str) -> bool:
    """Verify a file's checksum."""
    return generate_checksum(file_path) == expected


def format_checksum(checksum: str, length: int = 16) -> str:
    """Return a shortened version of a checksum."""
    return checksum[:length] + "..." if len(checksum) > length else checksum
