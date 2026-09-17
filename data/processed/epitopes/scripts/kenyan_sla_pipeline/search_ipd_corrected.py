#!/usr/bin/env python3
"""
CORRECTED: Search IPD-MHC for Kenyan SLA alleles
Uses the Latest branch and proper file checking
"""

import re
import csv
import os

FASTA_FILE = "data/raw/ipd_mhc/MHC_prot.fasta"

def check_fasta_file():
    """Verify FASTA file exists and has content"""
    if not os.path.exists(FASTA_FILE):
        return False, "File not found"
    
    size = os.path.getsize(FASTA_FILE)
    if size == 0:
        return False, "File is empty (size 0)"
    
    # Count sequences
    with open(FASTA_FILE, 'r') as f:
        seq_count = sum(1 for line in f if line.startswith('>'))
    
    if seq_count == 0:
        return False, "No sequences found (no '>' lines)"
    
    return True, f"Valid FASTA with {seq_count} sequences"

def main():
    print("="*80)
    print("SEARCH IPD-MHC FOR KENYAN SLA ALLELES")
    print("="*80)
    
    # Check file
    valid, msg = check_fasta_file()
    if not valid:
        print(f"❌ {msg}")
        print("   Please download the file first with:")
        print("   wget -O data/raw/ipd_mhc/MHC_prot.fasta \\")
        print("       https://raw.githubusercontent.com/ANHIG/IPDMHC/Latest/MHC_prot.fasta")
        return
    
    print(f"✅ {msg}")
    
    # List of Kenyan alleles to search
    alleles = [
        'SLA-1*1501',
        'SLA-1*1502',
        'SLA-1*0805',
        'SLA-1*rh03',
        'SLA-1*HB01',
        'SLA-2*0504',
        'SLA-2*05rh03',
        'SLA-2*HB04',
        'SLA-3*0601',
        'SLA-3*0502',
        'SLA-3*04hb06',
        # Known resolved from paper
        'SLA-1*22:01',
        'SLA-2*06:14',
        'SLA-2*06:15',
        'SLA-2*10:08',
        'SLA-3*05:03:03',
    ]
    
    print(f"\nSearching {len(alleles)} alleles in IPD-MHC...")
    
    found = []
    not_found = []
    
    with open(FASTA_FILE, 'r') as f:
        content = f.read()
    
    for allele in alleles:
        # Search for various patterns
        patterns = [
            allele,
            allele.replace('*', '*'),
            allele.replace('/', ''),
        ]
        
        matched = False
        for pattern in patterns:
            if pattern in content:
                # Find the full header
                # This is simplified - we'll extract more info later
                found.append(allele)
                matched = True
                break
        
        if not matched:
            not_found.append(allele)
    
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Found in IPD-MHC: {len(found)}")
    print(f"Not found: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️ Not found in IPD-MHC:")
        for allele in not_found:
            print(f"   - {allele}")
    
    print(f"\n✅ Search complete")
    print(f"\nNext steps:")
    print(f"1. For found alleles: Extract sequences and verify exact names")
    print(f"2. For not found alleles: Check GenBank accessions from paper")

if __name__ == "__main__":
    main()
