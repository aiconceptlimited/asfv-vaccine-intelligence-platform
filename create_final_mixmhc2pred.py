#!/usr/bin/env python3
"""
Create final MixMHC2pred submission with correct 12-aa context
Based on confirmed SLA_DRB1_02_02 allele from original HTL analysis
"""

import pandas as pd
import re

print("Loading junction data...")
junctions = pd.read_csv('construct_junctions_all.tsv', sep='\t')
sla_ii_junctions = junctions[junctions['assay_type'] == 'sla_ii']

print(f"Found {len(sla_ii_junctions):,} SLA-II junction records")

# Build context mapping
peptide_context = {}
processed = 0

for _, row in sla_ii_junctions.iterrows():
    peptide = row['peptide']
    processed += 1
    
    if processed % 100000 == 0:
        print(f"Processing record {processed:,}...")
    
    # Build full context
    full_context = row['left_epitope'] + row['linker'] + row['right_epitope']
    
    # Find peptide in context
    if peptide in full_context:
        pos = full_context.find(peptide)
        # Get 12-aa context: 6 before + peptide + 6 after
        start = max(0, pos - 6)
        end = min(len(full_context), pos + len(peptide) + 6)
        context = full_context[start:end]
        
        # Ensure exactly 12 characters
        if len(context) < 12:
            context = context.ljust(12, 'X')
        elif len(context) > 12:
            context = context[:12]
            
        peptide_context[peptide] = context

print(f"Created context for {len(peptide_context)} unique peptides")

# Read unique SLA-II peptides
with open('sla_ii_peptides.fasta', 'r') as f:
    content = f.read()
    peptides = re.findall(r'>.*\n([A-Z]+)', content)

print(f"Found {len(peptides)} unique SLA-II peptides")

# Create submission file
with open('sla_ii_mixmhc2pred_final.txt', 'w') as out:
    for peptide in peptides:
        context = peptide_context.get(peptide, 'X' * 12)
        out.write(f"{peptide}\t{context}\n")

print(f"\n✅ Created sla_ii_mixmhc2pred_final.txt")
print(f"   {len(peptides)} peptides with 12-aa context")
print(f"   Allele to use: SLA_DRB1_02_02 (confirmed from original HTL)")

# Verify
print("\nVerifying first 10 entries:")
with open('sla_ii_mixmhc2pred_final.txt', 'r') as f:
    for i, line in enumerate(f):
        if i < 10:
            parts = line.strip().split('\t')
            if len(parts) > 1:
                print(f"  {i+1}. Peptide: {parts[0][:10]}... Context: {parts[1]} (len: {len(parts[1])})")
        else:
            break

print("\n✅ All contexts are 12 amino acids long")
print("✅ Ready for MixMHC2pred with SLA_DRB1_02_02")

