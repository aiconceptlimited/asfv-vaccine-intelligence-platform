#!/usr/bin/env python3
"""
File I/O Utilities
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def ensure_directory(directory):
    """Ensure directory exists"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def read_manifest(manifest_path):
    """Read accession manifest file"""
    genomes = []
    path = Path(manifest_path)
    
    if not path.exists():
        logger.error(f"Manifest not found: {manifest_path}")
        return []
    
    with open(path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(',')
            if len(parts) < 5:
                logger.warning(f"Line {line_num}: Skipping malformed: {line}")
                continue
            
            try:
                genomes.append({
                    'accession': parts[0].strip(),
                    'strain': parts[1].strip(),
                    'country': parts[2].strip(),
                    'genotype': parts[3].strip(),
                    'year': int(parts[4].strip())
                })
            except ValueError:
                logger.warning(f"Line {line_num}: Invalid year: {parts[4].strip()}")
                continue
    
    logger.info(f"Loaded {len(genomes)} genomes from manifest")
    return genomes

def write_json(data, output_path):
    """Write JSON data to file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to write JSON: {e}")
        return False
