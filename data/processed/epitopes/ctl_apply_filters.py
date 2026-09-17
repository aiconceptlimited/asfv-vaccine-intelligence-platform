#!/usr/bin/env python3
import pandas as pd

# Load full ranked list
df = pd.read_csv('ctl_ranked_all.csv')

# Filter criteria:
# 1. Allele_Count >= 3 (multi-allele)
# 2. Conservation_Score >= 0.5 (at least 50% conserved)
# 3. Remove peptides with problematic sequences (optional)

filtered = df[(df['Allele_Count'] >= 3) & (df['Conservation_Score'] >= 0.5)]

print(f"Peptides after filters: {len(filtered)}")

# Select top 15
top15 = filtered.head(15)

# Save
top15.to_csv('ctl_final_candidates_filtered.csv', index=False)

print("\n=== FINAL CTL CANDIDATES (FILTERED, TOP 15) ===")
print(top15[['Rank', 'Protein', 'Peptide', 'Allele_Count', 'Conservation']])

print("\n=== PROTEIN DISTRIBUTION ===")
print(top15['Protein'].value_counts())

print("\n=== ALLELE COVERAGE DISTRIBUTION ===")
print(top15['Allele_Count'].value_counts().sort_index())
