#!/usr/bin/env python3
"""
Split NetMHCpan submission into one file per allele
Each file contains 494 peptides with the same allele
"""

from pathlib import Path
import re

# The 6 verified SLA-I alleles
alleles = [
    "SLA-1:0101",
    "SLA-1:0401", 
    "SLA-1:1201",
    "SLA-2:0401",
    "SLA-3:0301",
    "SLA-3:0401",
]

# Read the unique SLA-I peptides from fasta file
fasta_path = Path("sla_i_peptides.fasta")
fasta_content = fasta_path.read_text()
peptides = re.findall(r'>[^\n]*\n([A-Z]+)', fasta_content)

print(f"Found {len(peptides)} unique SLA-I peptides")
assert len(peptides) == 494, f"Expected 494 peptides, got {len(peptides)}"

# Create one file per allele
for allele in alleles:
    # Create safe filename (replace colon with underscore)
    safe_name = allele.replace(":", "_")
    output_path = Path("sla_i_batches") / f"{safe_name}.txt"
    
    # Write all peptides with this allele
    with output_path.open("w") as f:
        for peptide in peptides:
            f.write(f"{allele}\t{peptide}\n")
    
    # Count residues for this batch
    total_residues = sum(len(p) for p in peptides)
    print(f"{allele}: {len(peptides)} peptides, {total_residues} residues -> {output_path}")

print("\n✅ Created 6 allele-specific batch files")
print("   Each file has 494 lines and is ready for submission")
