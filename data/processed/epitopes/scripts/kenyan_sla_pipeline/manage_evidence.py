#!/usr/bin/env python3
"""
Manage SLA evidence — only verified data can be used
"""

import json
import sys
from datetime import datetime

def add_evidence():
    """Add new evidence record"""
    print("Add SLA evidence record")
    allele = input("Allele: ")
    value = input("Value (e.g., 0.89): ")
    source = input("Source (e.g., Sørensen et al. 2017): ")
    pmid = input("PMID: ")
    doi = input("DOI: ")
    freq_type = input("Frequency type (carrier/allele/haplotype): ")
    sample_size = input("Sample size: ")
    
    try:
        with open('data/curated/sla_evidence.json', 'r') as f:
            evidence = json.load(f)
    except:
        evidence = {}
    
    evidence[allele] = {
        'value': float(value),
        'source': source,
        'pmid': pmid,
        'doi': doi,
        'frequency_type': freq_type,
        'sample_size': int(sample_size),
        'verified': False,
        'verification_date': None,
        'notes': ''
    }
    
    with open('data/curated/sla_evidence.json', 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"✅ Added evidence for {allele} (unverified)")

def verify_evidence():
    """Mark evidence as verified"""
    allele = input("Allele to verify: ")
    
    try:
        with open('data/curated/sla_evidence.json', 'r') as f:
            evidence = json.load(f)
    except:
        print("❌ No evidence found")
        return
    
    if allele not in evidence:
        print(f"❌ Allele not found: {allele}")
        return
    
    evidence[allele]['verified'] = True
    evidence[allele]['verification_date'] = datetime.now().isoformat()
    
    with open('data/curated/sla_evidence.json', 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"✅ Verified: {allele}")

def show_evidence():
    """Show all evidence"""
    try:
        with open('data/curated/sla_evidence.json', 'r') as f:
            evidence = json.load(f)
    except:
        print("❌ No evidence found")
        return
    
    print("\n=== SLA EVIDENCE ===")
    for allele, info in evidence.items():
        status = "✅" if info['verified'] else "⚠️"
        print(f"{status} {allele}: {info['value']} ({info['frequency_type']}) from {info['source']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_evidence.py add     - Add new evidence")
        print("  python manage_evidence.py verify  - Verify evidence")
        print("  python manage_evidence.py show    - Show all evidence")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == 'add':
        add_evidence()
    elif command == 'verify':
        verify_evidence()
    elif command == 'show':
        show_evidence()
    else:
        print(f"Unknown command: {command}")
