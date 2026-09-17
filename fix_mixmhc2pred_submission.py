#!/usr/bin/env python3
"""
Fix MixMHC2pred submission - add 12-aa context for each junction peptide
"""

import pandas as pd
import re

# Load junctions to get context
junctions = pd.read_csv('construct_junctions_all.tsv', sep='\t')

# Get only SLA-II junctions (15mers)
sla_ii_junctions = junctions[junctions['assay_type'] == 'sla_ii']

print(f"Found {len(sla_ii_junctions)} SLA-II junction records")

# Build a mapping from peptide to context
# Context = left_epitope + linker + right_epitope
# We need 12 amino acids around the junction

peptide_context = {}

for _, row in sla_ii_junctions.iterrows():
    peptide = row['peptide']
    
    # Build the full context sequence
    left = row['left_epitope']
    linker = row['linker']
    right = row['right_epitope']
    full_context = left + linker + right
    
    # Find the peptide in the context
    if peptide in full_context:
        pos = full_context.find(peptide)
        # Get 12-aa context: 6 before + peptide + 6 after (or as much as available)
        context_start = max(0, pos - 6)
        context_end = min(len(full_context), pos + len(peptide) + 6)
        context_12 = full_context[context_start:context_end]
        # Pad if needed
        if len(context_12) < 12:
            context_12 = context_12.ljust(12, 'X')
        peptide_context[peptide] = context_12[:12]
    else:
        # Fallback: use adjacent amino acids if available
        peptide_context[peptide] = 'X' * 12

print(f"Created context for {len(peptide_context)} unique peptides")

# Now create the submission file
# Read the unique SLA-II peptides
with open('sla_ii_peptides.fasta', 'r') as f:
    content = f.read()
    peptides = re.findall(r'>.*\n([A-Z]+)', content)

print(f"Found {len(peptides)} unique SLA-II peptides")

with open('sla_ii_mixmhc2pred_submission.txt', 'w') as out:
    for peptide in peptides:
        context = peptide_context.get(peptide, 'X' * 12)
        out.write(f"{peptide}\t{context}\n")

print(f"\n✅ Created sla_ii_mixmhc2pred_submission.txt")
print(f"   {len(peptides)} peptides with context")
print(f"   Format: peptide<tab>12-aa context")

# Show examples
print(f"\nFirst 5 examples:")
with open('sla_ii_mixmhc2pred_submission.txt', 'r') as f:
    for i, line in enumerate(f):
        if i < 5:
            parts = line.strip().split('\t')
            print(f"  {i+1}. {parts[0][:10]}... | {parts[1] if len(parts) > 1 else 'NO CONTEXT'}")
        else:
            break
