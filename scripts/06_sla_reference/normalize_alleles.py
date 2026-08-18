#!/usr/bin/env python3
"""
Normalize SLA allele names from FASTA headers
Converts IPD-MHC nomenclature (e.g., SLA-1*14:05) to canonical format
"""

import re

def normalize_allele(allele_name):
    """
    Normalize allele name to a canonical format.
    Handles:
    - SLA-1*14:05 → SLA-1*14:05 (keep as is)
    - SLA-1*1405 → SLA-1*14:05 (insert colon)
    - SLA-1*14:05:01 → SLA-1*14:05 (remove extra digits)
    """
    if not allele_name:
        return allele_name
    
    # Remove whitespace
    allele_name = allele_name.strip()
    
    # Check for locus and allele parts
    match = re.match(r'^([A-Z0-9-]+)\*([0-9:]+)$', allele_name)
    if match:
        locus = match.group(1)
        allele = match.group(2)
        # If allele has no colon and is 4 digits, insert colon
        if ':' not in allele and len(allele) == 4:
            allele = f"{allele[:2]}:{allele[2:]}"
        # If allele has more than 2 parts, keep first two
        parts = allele.split(':')
        if len(parts) > 2:
            allele = f"{parts[0]}:{parts[1]}"
        return f"{locus}*{allele}"
    
    return allele_name

# Test with examples
test_names = [
    "SLA-1*14:05",
    "SLA-1*1405",
    "SLA-1*14:05:01",
    "SLA-DQB1*01:05",
    "SLA-DQB1*0105",
    "SLA-DRB1*04:06:01"
]

print("=== Allele Normalization Test ===")
for name in test_names:
    normalized = normalize_allele(name)
    print(f"  {name} → {normalized}")
