#!/usr/bin/env python3
"""
Retrieve SLA sequences from IPD-MHC for verified Kenyan alleles
"""

import json
import requests
import hashlib
from datetime import datetime
import os

# Verified Kenyan alleles
alleles = [
    'SLA-1*1501/1502',
    'SLA-2*NS#16', 
    'SLA-3*04hb06',
    'SLA-1*0805',
    'SLA-2*0504',
    'SLA-3*0601',
    'SLA-1*rh03',
    'SLA-2*05rh03',
    'SLA-1*HB01',
    'SLA-2*HB04',
    'SLA-3*0502'
]

# IPD-MHC API base URL
base_url = "https://www.ebi.ac.uk/ipd/mhc/api/sla/alleles"

print("="*80)
print("RETRIEVE SLA SEQUENCES FROM IPD-MHC")
print("="*80)

sequences = {}
missing = []

for allele in alleles:
    print(f"\nSearching for: {allele}")
    
    # Try different search formats
    search_terms = [
        allele,
        allele.replace('*', '*'),
        allele.split('*')[0] + '*' + allele.split('*')[1].replace('/', '')
    ]
    
    found = False
    for term in search_terms:
        try:
            url = f"{base_url}?search={term}"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data and 'results' in data and data['results']:
                    # Take first result
                    result = data['results'][0]
                    seq = result.get('protein_sequence', '')
                    if seq:
                        sequences[allele] = {
                            'allele': allele,
                            'official_name': result.get('name', allele),
                            'sequence': seq,
                            'length': len(seq),
                            'accession': result.get('accession', 'unknown'),
                            'source': 'IPD-MHC API',
                            'retrieval_date': datetime.now().isoformat(),
                            'checksum': hashlib.sha256(seq.encode()).hexdigest()[:16],
                            'verified': True
                        }
                        print(f"  ✅ Found: {sequences[allele]['official_name']} ({len(seq)} aa)")
                        found = True
                        break
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            continue
    
    if not found:
        print(f"  ❌ Not found in IPD-MHC")
        missing.append(allele)

# Save sequences
os.makedirs('data/verified/kenyan_sla', exist_ok=True)
with open('data/verified/kenyan_sla/sla_sequences.json', 'w') as f:
    json.dump(sequences, f, indent=2)

print(f"\n✅ Retrieved {len(sequences)} sequences")
if missing:
    print(f"⚠️ Missing {len(missing)} sequences: {missing}")

# Also save a FASTA file for NetMHCpan
with open('data/verified/kenyan_sla/sla_sequences.fasta', 'w') as f:
    for allele, info in sequences.items():
        f.write(f">{allele}|{info['official_name']}\n{info['sequence']}\n")

print("✅ FASTA file created: data/verified/kenyan_sla/sla_sequences.fasta")
