#!/usr/bin/env python3
"""
Download Utilities Module
Helper functions for genome acquisition

Functions:
- read_manifest: Read accession manifest
- validate_accession: Validate accession format
- ensure_directory: Create output directories
- calculate_checksum: Calculate file checksum
- verify_file: Verify downloaded file
- write_report: Write JSON report
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from Bio import SeqIO

logger = logging.getLogger(__name__)

def read_manifest(manifest_path):
    """
    Read accession manifest file
    
    Format: accession,strain,country,genotype,year
    
    Args:
        manifest_path: Path to manifest file
    
    Returns:
        list: List of genome dictionaries
    """
    genomes = []
    
    if not Path(manifest_path).exists():
        logger.error(f"Manifest not found: {manifest_path}")
        return []
    
    with open(manifest_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(',')
            if len(parts) < 5:
                logger.warning(f"Line {line_num}: Skipping malformed entry: {line}")
                continue
            
            try:
                genomes.append({
                    'accession': parts[0].strip(),
                    'strain': parts[1].strip(),
                    'country': parts[2].strip(),
                    'genotype': parts[3].strip(),
                    'year': int(parts[4].strip())
                })
            except ValueError as e:
                logger.warning(f"Line {line_num}: Invalid year format: {parts[4].strip()} - {e}")
                continue
    
    logger.info(f"Loaded {len(genomes)} genomes from manifest")
    return genomes

def validate_accession(accession):
    """
    Validate NCBI accession format
    
    Args:
        accession: NCBI accession string
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic validation: non-empty, alphanumeric with optional version
    if not accession or not isinstance(accession, str):
        return False
    
    # Check for version suffix (e.g., .1)
    acc = accession.split('.')[0]
    
    # Typical NCBI accession patterns
    # RefSeq: AC_123456, NC_123456, NG_123456, NT_123456, NW_123456, NZ_123456, NM_123456, NR_123456, XM_123456, XR_123456
    # GenBank: A00001, A00001.1, etc.
    
    if len(acc) < 4:
        return False
    
    # Check that it contains alphanumeric characters
    if not acc.replace('_', '').isalnum():
        return False
    
    return True

def ensure_directory(directory):
    """
    Ensure directory exists
    
    Args:
        directory: Path to directory
    
    Returns:
        Path: Directory path
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def calculate_checksum(file_path):
    """
    Calculate SHA256 checksum of file
    
    Args:
        file_path: Path to file
    
    Returns:
        str: SHA256 checksum
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def verify_file(file_path, min_size=1000):
    """
    Verify downloaded file
    
    Args:
        file_path: Path to file
        min_size: Minimum file size in bytes
    
    Returns:
        dict: Verification result
    """
    path = Path(file_path)
    
    result = {
        'exists': path.exists(),
        'size_bytes': path.stat().st_size if path.exists() else 0,
        'is_valid': False,
        'can_parse': False
    }
    
    if not result['exists']:
        return result
    
    if result['size_bytes'] < min_size:
        return result
    
    result['is_valid'] = True
    
    # Try to parse as GenBank or FASTA
    try:
        records = list(SeqIO.parse(path, "genbank"))
        result['can_parse'] = len(records) > 0
        result['record_count'] = len(records)
        result['format'] = 'genbank'
    except:
        try:
            records = list(SeqIO.parse(path, "fasta"))
            result['can_parse'] = len(records) > 0
            result['record_count'] = len(records)
            result['format'] = 'fasta'
        except:
            result['can_parse'] = False
    
    result['is_valid'] = result['is_valid'] and result['can_parse']
    
    if result['is_valid']:
        result['checksum'] = calculate_checksum(path)
    
    return result

def write_report(report_data, output_path):
    """
    Write JSON report
    
    Args:
        report_data: Dictionary to write
        output_path: Output file path
    
    Returns:
        bool: True if successful
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        logger.info(f"Report written to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write report: {e}")
        return False

def get_config_value(config, key_path, default=None):
    """
    Get nested configuration value
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path (e.g., 'project.name')
        default: Default value if not found
    
    Returns:
        Value or default
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value
