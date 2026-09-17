#!/usr/bin/env python3
import pandas as pd
import numpy as np

# Load representatives
df = pd.read_csv('ctl_cluster_representatives.csv')

print(f"Loaded {len(df)} representatives")

# Parse conservation scores
def parse_conservation(cons):
    if pd.isna(cons) or cons == 'N/A':
        return 0
    if isinstance(cons, str) and '/' in cons:
        try:
            num, den = cons.split('/')
            return int(num) / int(den) if int(den) > 0 else 0
        except:
            return 0
    return 0

df['Conservation_Score'] = df['Conservation'].apply(parse_conservation)

# Normalize allele count (max 6)
df['Allele_Score'] = df['Allele_Count'] / 6.0

# Combine scores
# Weight: Allele 50%, Conservation 30%, Cluster Size 20%
df['Rank_Score'] = (df['Allele_Score'] * 0.5) + \
                   (df['Conservation_Score'] * 0.3) + \
                   (df['Cluster_Size'] / max(df['Cluster_Size']) * 0.2 if max(df['Cluster_Size']) > 0 else 0)

# Sort by rank score
df = df.sort_values('Rank_Score', ascending=False).reset_index(drop=True)
df['Rank'] = range(1, len(df) + 1)

# Select top candidates
top_n = 50
top_candidates = df.head(top_n)

# Save results
df.to_csv('ctl_ranked_all.csv', index=False)
top_candidates.to_csv('ctl_top50_candidates.csv', index=False)

print(f"Ranked {len(df)} candidates")
print(f"Top {top_n} candidates saved to ctl_top50_candidates.csv")

print("\n=== TOP 20 CANDIDATES ===")
print(top_candidates[['Rank', 'Protein', 'Peptide', 'Allele_Count', 'Conservation', 'Rank_Score']].head(20))

print("\n=== PROTEIN DISTRIBUTION IN TOP 50 ===")
print(top_candidates['Protein'].value_counts())

print("\n=== ALLELE COVERAGE DISTRIBUTION IN TOP 50 ===")
print(top_candidates['Allele_Count'].value_counts().sort_index())
