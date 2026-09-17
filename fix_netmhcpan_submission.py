#!/usr/bin/env python3
"""
Fix NetMHCpan submission - correctly parse alleles from your frozen panel
"""

import pandas as pd
import re

# Read the core panel
df = pd.read_csv('data/processed/epitopes/core_panel_11_FINAL.csv')

print("Columns found:", df.columns.tolist())

# Try to identify allele and class columns
allele_col = None
class_col = None

for col in df.columns:
    if 'allele' in col.lower():
        allele_col = col
    if 'class' in col.lower():
        class_col = col

print(f"Allele column: {allele_col}")
print(f"Class column: {class_col}")

# Extract Class I alleles
if allele_col and class_col:
    class_i_alleles = df[df[class_col].astype(str).str.upper() == 'I'][allele_col].tolist()
else:
    # Fallback: try to infer
    class_i_alleles = []
    for _, row in df.iterrows():
        # Check if any column contains 'I' or 'Class I'
        row_str = ' '.join([str(v) for v in row.values])
        if 'I' in row_str or 'Class I' in row_str:
            # Find the allele value
            for col in df.columns:
                if 'allele' in col.lower() and pd.notna(row[col]):
                    class_i_alleles.append(row[col])
                    break

print(f"Found {len(class_i_alleles)} Class I alleles:")
print(f"  {class_i_alleles}")

# Read SLA-I peptides
with open('sla_i_peptides.fasta', 'r') as f:
    content = f.read()
    peptides = re.findall(r'>.*\n([A-Z]+)', content)

print(f"Found {len(peptides)} SLA-I peptides")

# Create submission file in the correct format
with open('sla_i_netmhcpan_submission.txt', 'w') as out:
    for allele in class_i_alleles:
        for peptide in peptides:
            out.write(f"{allele}\t{peptide}\n")

print(f"\n✅ Created sla_i_netmhcpan_submission.txt")
print(f"   {len(class_i_alleles)} alleles × {len(peptides)} peptides = {len(class_i_alleles) * len(peptides):,} lines")
print(f"   Format: allele<tab>peptide")
