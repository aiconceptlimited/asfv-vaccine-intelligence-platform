#!/usr/bin/env python3
"""
DETAILED SEARCH: Find Kenyan alleles in IPD-MHC and extract sequences
"""

import re
import csv
import os
import json
from pathlib import Path

FASTA_FILE = "data/raw/ipd_mhc/MHC_prot.fasta"
OUTPUT_DIR = "data/verified/kenyan_sla"

def search_alleles_in_fasta(fasta_file, search_terms):
    """Search for alleles in FASTA file"""
    results = {}
    
    # Read the entire file
    with open(fasta_file, 'r') as f:
        content = f.read()
    
    # Split into records
    records = content.split('>')[1:]  # Skip first empty split
    
    for term in search_terms:
        print(f"\nSearching: {term}")
        term_clean = term.replace('*', '').replace('/', '').replace(':', '')
        
        found = False
        for record in records:
            header = record.split('\n')[0]
            sequence = ''.join(record.split('\n')[1:])
            
            # Check if term matches in header
            if term in header or term_clean in header:
                # Extract allele name
                allele_match = re.search(r'(SLA-[0-9]+\*[^\s]+)', header)
                allele_name = allele_match.group(1) if allele_match else 'Unknown'
                
                # Extract accession
                accession_match = re.search(r'accession:([^\s]+)', header)
                accession = accession_match.group(1) if accession_match else 'Unknown'
                
                results[term] = {
                    'search_term': term,
                    'allele_name': allele_name,
                    'accession': accession,
                    'sequence': sequence[:100] + '...' if len(sequence) > 100 else sequence,
                    'length': len(sequence),
                    'header': header,
                    'found': True,
                    'status': 'resolved'
                }
                print(f"  ✅ Found: {allele_name} (accession: {accession}, length: {len(sequence)} aa)")
                found = True
                break
        
        if not found:
            results[term] = {
                'search_term': term,
                'found': False,
                'status': 'not_found_in_ipd'
            }
            print(f"  ❌ Not found in IPD-MHC")
    
    return results

# List of Kenyan alleles to search
kenyan_alleles = [
    # Hp-F.0 haplotype
    'SLA-1*1501',
    'SLA-1*1502',
    'SLA-1*1501/1502',  # Paper designation
    'SLA-2*NS#16',      # Novel allele
    'SLA-3*04hb06',     # Paper designation
    
    # Hp-6.0 haplotype
    'SLA-1*0805',
    'SLA-2*0504',
    'SLA-3*0601',
    
    # Hp-G.0 haplotype
    'SLA-1*rh03',
    'SLA-2*05rh03',
    
    # Hp-H.0 haplotype
    'SLA-1*HB01',
    'SLA-2*HB04',
    'SLA-3*0502',
    
    # Resolved alleles from paper
    'SLA-1*22:01',      # NS#3
    'SLA-2*06:14',      # NS#2
    'SLA-2*06:15',      # NS#10
    'SLA-2*10:08',      # NS#7
    'SLA-3*05:03:03',   # NS#9
]

print("="*80)
print("DETAILED SEARCH OF IPD-MHC FOR KENYAN SLA ALLELES")
print("="*80)
print(f"Database: {FASTA_FILE}")

# Check file exists
if not os.path.exists(FASTA_FILE):
    print(f"❌ FASTA file not found: {FASTA_FILE}")
    exit(1)

file_size = os.path.getsize(FASTA_FILE)
print(f"File size: {file_size / (1024*1024):.1f} MB")

# Count sequences
with open(FASTA_FILE, 'r') as f:
    seq_count = sum(1 for line in f if line.startswith('>'))
print(f"Total sequences: {seq_count}")

# Search
print(f"\nSearching {len(kenyan_alleles)} alleles...")
results = search_alleles_in_fasta(FASTA_FILE, kenyan_alleles)

# Save results
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(f"{OUTPUT_DIR}/ipd_search_results.json", 'w') as f:
    json.dump(results, f, indent=2, default=str)

# Summary
print("\n" + "="*80)
print("SEARCH SUMMARY")
print("="*80)

found_count = sum(1 for r in results.values() if r.get('found', False))
not_found_count = len(results) - found_count

print(f"Found in IPD-MHC: {found_count}")
print(f"Not found: {not_found_count}")

print("\n✅ Found alleles:")
for term, result in results.items():
    if result.get('found', False):
        print(f"  ✅ {term} → {result['allele_name']} (accession: {result['accession']})")

print("\n❌ Not found in IPD-MHC:")
for term, result in results.items():
    if not result.get('found', False):
        print(f"  ❌ {term}")

print(f"\n✅ Results saved to: {OUTPUT_DIR}/ipd_search_results.json")
