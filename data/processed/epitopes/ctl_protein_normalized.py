#!/usr/bin/env python3
import pandas as pd

# Load reference lengths
ref_lengths = {
    'p30': 179,
    'p54': 172,
    'p72': 632,
    'pcp312r': 285,
    'cd2v': 371,
    'pp220': 2477
}

# Load verified candidates (from ctl_peptides_clean.txt or similar)
# Load top 15
top15 = pd.read_csv('ctl_final_candidates_filtered.csv')

# Count verified candidates per protein
verified_counts = {
    'p30': 14,
    'p54': 10,
    'pcp312r': 20,
    'cd2v': 22,
    'pp220': 199
}

print("=== PROTEIN-NORMALIZED ANALYSIS ===")
print(f"{'Protein':<10} {'Length':<8} {'Verified':<10} {'Per100aa':<10} {'Top15':<8}")
print("-" * 50)

for protein in ['p30', 'p54', 'pcp312r', 'cd2v', 'pp220']:
    length = ref_lengths.get(protein, 0)
    verified = verified_counts.get(protein, 0)
    per100 = (verified / length) * 100 if length > 0 else 0
    top15_count = len(top15[top15['Protein'] == protein])
    print(f"{protein:<10} {length:<8} {verified:<10} {per100:<10.2f} {top15_count:<8}")

print("\n=== PP220 ENRICHMENT ASSESSMENT ===")
pp220_per100 = (199 / 2477) * 100
avg_per100 = sum([(verified_counts.get(p, 0) / ref_lengths.get(p, 1)) * 100 for p in ['p30', 'p54', 'pcp312r', 'cd2v']]) / 4
print(f"PP220 candidates per 100aa: {pp220_per100:.2f}")
print(f"Average other proteins per 100aa: {avg_per100:.2f}")
print(f"Enrichment ratio: {pp220_per100 / avg_per100:.2f}x")
