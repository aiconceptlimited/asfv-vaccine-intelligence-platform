#!/usr/bin/env python3
"""
Accession Validation Utilities
"""

def validate_accession(accession):
    """
    Validate NCBI accession format
    Returns True if valid, False otherwise
    """
    if not accession or not isinstance(accession, str):
        return False
    
    acc = accession.split('.')[0]
    
    if len(acc) < 4:
        return False
    
    if not acc.replace('_', '').isalnum():
        return False
    
    return True
