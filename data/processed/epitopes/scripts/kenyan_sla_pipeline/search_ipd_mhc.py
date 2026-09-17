#!/usr/bin/env python3
"""
Search IPD-MHC protein FASTA for Kenyan SLA alleles
"""

import re
import os
import hashlib
from datetime import datetime

# Kenyan alleles to search (using likely official formats)
search_terms = [
    'SLA-1*15:01',
    'SLA-1*15:02',
    'SLA-1*08:05',
    'SLA-1*rh03',
    'SLA-1*HB01',
    'SLA-2*05:04',
    'SLA-2*05rh03',
    'SLA-2*HB04',
    'SLA-3*06:01',
    'SLA-3*05:02',
    'SLA-3*04hb06',
    'SLA-1*22:01',      # NS#3
    'SLA-2*06:14',      # NS#2
    'SLA-2*06:15',      # NS#10
    'SLA-2*10:08',      # NS#7
    'SLA-3*05:03:03',   # NS#9
]

print("="*80)
print("SEARCH IPD-MHC FOR KENYAN SLA ALLELES")
print("="*80)

fasta_file = 'data/raw/ipd_mhc/MHC_prot.fasta'
if not os.path.exists(fasta_file):
    print(f"❌ FASTA file not found: {fasta_file}")
    print("   Please download it first.")
    exit(1)

print(f"\n✅ FASTA file found: {fasta_file}")

# Parse FASTA file
def parse_fasta(filename):
    sequences = {}
    current_header = None
    current_seq = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_header:
                    sequences[current_header] = ''.join(current_seq)
                current_header = line[1:]
                current_seq = []
            else:
                current_seq.append(line)
        if current_header:
            sequences[current_header] = ''.join(current_seq)
    
    return sequences

print("\nParsing FASTA file...")
sequences = parse_fasta(fasta_file)
print(f"Total sequences: {len(sequences)}")

# Search for each allele
print("\n=== SEARCH RESULTS ===")
found = []
not_found = []

for term in search_terms:
    print(f"\nSearching: {term}")
    matched = False
    for header, seq in sequences.items():
        if term in header or term.replace(':', '') in header:
            # Get the allele name from header
            allele_match = re.search(r'(SLA-[0-9]+\*[^\s]+)', header)
            allele_name = allele_match.group(1) if allele_match else term
            
            # Get accession if present
            accession_match = re.search(r'accession:([^\s]+)', header)
            accession = accession_match.group(1) if accession_match else 'unknown'
            
            print(f"  ✅ Found: {allele_name}")
            print(f"     Accession: {accession}")
            print(f"     Length: {len(seq)} aa")
            print(f"     Header: {header[:80]}...")
            
            found.append({
                'search_term': term,
                'official_name': allele_name,
                'accession': accession,
                'sequence': seq,
                'length': len(seq),
                'header': header
            })
            matched = True
            break
    
    if not matched:
        print(f"  ❌ Not found")
        not_found.append(term)

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Found: {len(found)} alleles")
print(f"Not found: {len(not_found)} alleles")

if not_found:
    print("\nNot found alleles:")
    for term in not_found:
        print(f"  - {term}")

# Save found sequences
if found:
    with open('data/verified/kenyan_sla/ipd_mhc_found.fasta', 'w') as f:
        for item in found:
            f.write(f">{item['official_name']}|{item['accession']}\n{item['sequence']}\n")
    
    print("\n✅ Found sequences saved to: data/verified/kenyan_sla/ipd_mhc_found.fasta")
    
    # Also save as JSON with metadata
    import json
    with open('data/verified/kenyan_sla/ipd_mhc_found.json', 'w') as f:
        json.dump(found, f, indent=2, default=str)

print("\n⚠️ Note: Not finding an allele doesn't mean it doesn't exist.")
print("   The official name may use different formatting (e.g., SLA-1*15:01 vs SLA-1*1501).")
