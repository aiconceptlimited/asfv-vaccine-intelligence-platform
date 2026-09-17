#!/usr/bin/env python3
"""
Genome Validation Utilities
"""

import logging
from pathlib import Path
from Bio import SeqIO

logger = logging.getLogger(__name__)

def verify_genome_file(file_path, min_size=1000):
    """Verify downloaded genome file"""
    path = Path(file_path)
    
    result = {
        'exists': path.exists(),
        'size_bytes': path.stat().st_size if path.exists() else 0,
        'is_valid': False,
        'can_parse': False
    }
    
    if not result['exists'] or result['size_bytes'] < min_size:
        return result
    
    result['is_valid'] = True
    
    for fmt in ['genbank', 'fasta']:
        try:
            records = list(SeqIO.parse(path, fmt))
            if records:
                result['can_parse'] = True
                result['record_count'] = len(records)
                result['format'] = fmt
                break
        except:
            continue
    
    result['is_valid'] = result['is_valid'] and result['can_parse']
    return result
