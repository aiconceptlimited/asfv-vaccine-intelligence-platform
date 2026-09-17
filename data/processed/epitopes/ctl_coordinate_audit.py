#!/usr/bin/env python3
import pandas as pd

# Load top 15
top15 = pd.read_csv('ctl_final_candidates_filtered.csv')

# Load pp220 reference to find positions
ref_file = 'pp220/ctl/pp220_reference_clean.txt'
try:
    with open(ref_file, 'r') as f:
        ref_seq = f.read().strip()
except:
    ref_seq = ""

print("=== COORDINATE AUDIT ===")
print("Finding positions for pp220 candidates in reference sequence...\n")

pp220_candidates = top15[top15['Protein'] == 'pp220']

for idx, row in pp220_candidates.iterrows():
    peptide = row['Peptide']
    if ref_seq:
        pos = ref_seq.find(peptide)
        if pos != -1:
            print(f"  {peptide}: position {pos+1}")
        else:
            print(f"  {peptide}: NOT FOUND in reference")

print("\n=== SUGGESTED REGIONAL INDEPENDENCE ===")
print("Based on positions, check if candidates are clustered or spread out.")
print("Candidates within 20aa of each other may be redundant.")
