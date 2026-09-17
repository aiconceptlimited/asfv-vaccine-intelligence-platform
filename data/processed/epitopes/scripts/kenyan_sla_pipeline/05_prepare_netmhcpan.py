#!/usr/bin/env python3
"""
Stage 5: Prepare NetMHCpan Input
Creates input files for NetMHCpan
"""

import pandas as pd
import os
import sys

print("=" * 80)
print("STAGE 5: PREPARE NETMHCPAN INPUT")
print("=" * 80)

# CTL peptides
peptides = ['HIDKNIIQY', 'RSIPLANIY', 'YTDIVQKKY']

print(f"\nPeptides: {len(peptides)}")
for peptide in peptides:
    print(f"  - {peptide}")

# Create input file
input_file = "netmhcpan_input.fasta"
with open(input_file, 'w') as f:
    f.write("# NetMHCpan-4.1 Input\n")
    f.write("# Kenyan SLA Alleles\n")
    f.write("# Peptides: HIDKNIIQY, RSIPLANIY, YTDIVQKKY\n\n")
    for peptide in peptides:
        f.write(f">{peptide}\n")
        f.write(f"{peptide}\n")

print(f"\n✅ Input file created: {input_file}")

print("\n⚠️ This file must be submitted to NetMHCpan-4.1")
print("   URL: https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/")
print("   Input Type: PEPTIDE")
print("   Custom MHC: Paste SLA sequences")

print("\n✅ Placeholder: Stage 5 complete (manual submission required)")
