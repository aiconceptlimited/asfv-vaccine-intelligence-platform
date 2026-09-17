#!/usr/bin/env python3
"""
Stage 3: Retrieve SLA Sequences
Gets full protein sequences from IPD-MHC
"""

import pandas as pd
import os
import sys

print("=" * 80)
print("STAGE 3: RETRIEVE SLA SEQUENCES")
print("=" * 80)

# Load evidence table
df = pd.read_csv('sla_frequency_evidence.csv')
alleles = df['allele'].unique()

print(f"\nAlleles to retrieve: {len(alleles)}")
for allele in alleles:
    print(f"  - {allele}")

print("\n⚠️ This stage requires manual retrieval from IPD-MHC")
print("   URL: https://www.ebi.ac.uk/ipd/mhc/sla/")
print("\nFor each allele, copy the full protein sequence")
print("   into sla_sequences.fasta")

print("\n✅ Placeholder: Stage 3 complete (manual sequence retrieval required)")
