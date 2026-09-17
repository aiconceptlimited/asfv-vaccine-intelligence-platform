#!/usr/bin/env python3
"""
Properly format MixMHC2pred input with correct 12-aa context
"""

import pandas as pd
import re

# Load junctions
print("Loading junction data...")
junctions = pd.read_csv('construct_junctions_all.tsv', sep='\t')
sla_ii_junctions = junctions[junctions['assay_type'] == 'sla_ii']

print(f"Found {len(sla_ii_junctions)} SLA-II junction records")

# Build context mapping
peptide_context = {}
processed_count = 0

for _, row in sla_ii_junctions.iterrows():
    peptide = row['peptide']
    processed_count += 1
    
    if processed_count % 100000 == 0:
        print(f"Processing record {processed_count:,}...")
    
    # Build full context: left_epitope + linker + right_epitope
    full_context = row['left_epitope'] + row['linker'] + row['right_epitope']
    
    # Find peptide in context
    if peptide in full_context:
        pos = full_context.find(peptide)
        # Get 12-aa context: 6 before + peptide + 6 after
        start = max(0, pos - 6)
        end = min(len(full_context), pos + len(peptide) + 6)
        context = full_context[start:end]
        
        # Pad to exactly 12 characters if needed
        if len(context) < 12:
            context = context.ljust(12, 'X')
        elif len(context) > 12:
            # Truncate to 12
            context = context[:12]
            
        peptide_context[peptide] = context

print(f"Created context for {len(peptide_context)} unique peptides")

# Read unique SLA-II peptides
with open('sla_ii_peptides.fasta', 'r') as f:
    content = f.read()
    peptides = re.findall(r'>.*\n([A-Z]+)', content)

print(f"Found {len(peptides)} unique SLA-II peptides")

# Create properly formatted submission file
with open('sla_ii_mixmhc2pred_fixed.txt', 'w') as out:
    for peptide in peptides:
        context = peptide_context.get(peptide, 'X' * 12)
        # Format: peptide<tab>12-aa context
        out.write(f"{peptide}\t{context}\n")

print(f"\n✅ Created sla_ii_mixmhc2pred_fixed.txt")
print(f"   {len(peptides)} peptides with 12-aa context")

# Verify context lengths
print("\nVerifying context lengths:")
with open('sla_ii_mixmhc2pred_fixed.txt', 'r') as f:
    for i, line in enumerate(f):
        if i < 10:
            parts = line.strip().split('\t')
            if len(parts) > 1:
                print(f"  Peptide: {parts[0][:10]}... Context: {parts[1]} (len: {len(parts[1])})")
        else:
            break

print(f"\n✅ All contexts are 12 amino acids long")

