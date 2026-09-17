#!/usr/bin/env python3
"""
Coordinate-aware conservation analysis for p30 candidates
"""

import sys
import re
from collections import defaultdict

# Read the alignment file
alignment_file = "/home/abubakar/asfv_vaccine_platform/data/processed/alignments/CP204L_p30_all_aligned.fasta"

# Read sequences and headers
headers = []
sequences = []
current_header = ""
current_seq = ""

with open(alignment_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if current_header:
                headers.append(current_header)
                sequences.append(current_seq)
            current_header = line
            current_seq = ""
        else:
            current_seq += line
    if current_header:
        headers.append(current_header)
        sequences.append(current_seq)

# Find the reference sequence (MW856067)
ref_idx = None
for i, h in enumerate(headers):
    if 'MW856067' in h:
        ref_idx = i
        break

if ref_idx is None:
    print("ERROR: MW856067 reference sequence not found")
    sys.exit(1)

ref_seq = sequences[ref_idx]
ref_header = headers[ref_idx]

# Remove gaps from reference to get ungapped positions
ref_ungapped = ref_seq.replace('-', '')
print(f"Reference: {ref_header}")
print(f"Alignment length: {len(ref_seq)}")
print(f"Ungapped length: {len(ref_ungapped)}")
print()

# Create mapping: alignment position -> ungapped position
pos_map = {}
ungapped_pos = 1
for i, char in enumerate(ref_seq):
    if char != '-':
        pos_map[ungapped_pos] = i
        ungapped_pos += 1

# Read candidate peptides from p30_mapped_final.tsv
candidates = []
with open('p30_mapped_final.tsv', 'r') as f:
    lines = f.readlines()
    for line in lines[1:]:  # skip header
        parts = line.strip().split('\t')
        if len(parts) >= 10 and parts[9] == 'MAPPED':
            peptide = parts[0]
            start = int(parts[2])
            end = int(parts[3])
            breadth = parts[4]
            bindlevel = parts[8]
            candidates.append((peptide, start, end, breadth, bindlevel))

print(f"Candidates to analyze: {len(candidates)}")
print()

# Analyze each candidate
print("Peptide\tStart\tEnd\tSLA_Breadth\tBindLevel\tConservation\tVariants\tStatus")
for peptide, start, end, breadth, bindlevel in candidates:
    # Get alignment positions for this peptide
    aln_start = pos_map.get(start)
    aln_end = pos_map.get(end)
    
    if aln_start is None or aln_end is None:
        print(f"{peptide}\t{start}\t{end}\t{breadth}\t{bindlevel}\t-\t-\tMAPPING_ERROR")
        continue
    
    # Extract the peptide from each sequence at these coordinates
    variants = []
    conserved_count = 0
    
    for i, seq in enumerate(sequences):
        # Get the segment from alignment
        segment = seq[aln_start:aln_end+1]
        # Remove gaps
        segment_clean = segment.replace('-', '')
        
        if segment_clean == peptide:
            conserved_count += 1
        else:
            variants.append(f"{headers[i].split()[0][1:]}:{segment_clean}")
    
    total = len(sequences)
    conservation = f"{conserved_count}/{total} ({conserved_count*100//total}%)"
    
    if conserved_count == total:
        status = "CONSERVED"
    elif conserved_count >= total * 0.9:
        status = "HIGHLY_CONSERVED"
    elif conserved_count >= total * 0.7:
        status = "MODERATE"
    else:
        status = "VARIABLE"
    
    # Limit variants display
    variant_str = ", ".join(variants[:3])
    if len(variants) > 3:
        variant_str += f" +{len(variants)-3} more"
    
    print(f"{peptide}\t{start}\t{end}\t{breadth}\t{bindlevel}\t{conservation}\t{variant_str}\t{status}")
