#!/usr/bin/env python3
"""
Checksum Utilities
"""

import hashlib

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
