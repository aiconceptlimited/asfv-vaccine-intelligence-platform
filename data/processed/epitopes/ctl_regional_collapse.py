#!/usr/bin/env python3
import pandas as pd
import re

# Load top 50 candidates
df = pd.read_csv('ctl_top50_candidates.csv')

# Focus on pp220 candidates
pp220_df = df[df['Protein'] == 'pp220'].copy()
print(f"PP220 candidates in top 50: {len(pp220_df)}")

def calculate_overlap(seq1, seq2):
    seq1, seq2 = str(seq1), str(seq2)
    max_overlap = 0
    for shift in range(1, min(len(seq1), len(seq2))):
        if seq1[-shift:] == seq2[:shift]:
            max_overlap = max(max_overlap, shift)
        if seq2[-shift:] == seq1[:shift]:
            max_overlap = max(max_overlap, shift)
    return max_overlap

def cluster_peptides(peptides, min_overlap=8):
    clusters = []
    used = set()
    for i, pep1 in enumerate(peptides):
        if i in used:
            continue
        cluster = [i]
        used.add(i)
        for j, pep2 in enumerate(peptides):
            if j in used:
                continue
            if calculate_overlap(pep1, pep2) >= min_overlap:
                cluster.append(j)
                used.add(j)
        clusters.append(cluster)
    return clusters

# Get pp220 peptides
pp220_peptides = pp220_df['Peptide'].tolist()
clusters = cluster_peptides(pp220_peptides, min_overlap=8)

print(f"PP220 clusters: {len(clusters)}")
print(f"PP220 clusters with >1 peptide: {len([c for c in clusters if len(c) > 1])}")

# Select representatives from each cluster
representatives = []
for idx, cluster in enumerate(clusters):
    cluster_peps = [pp220_peptides[i] for i in cluster]
    # Select the one with highest rank (lowest rank number = best)
    best_rank = min([pp220_df[pp220_df['Peptide'] == p]['Rank'].values[0] for p in cluster_peps])
    best_pep = pp220_df[pp220_df['Rank'] == best_rank]['Peptide'].values[0]
    representatives.append({
        'Original_Cluster': idx + 1,
        'Cluster_Size': len(cluster),
        'Representative': best_pep,
        'Rank': best_rank,
        'Members': ';'.join(cluster_peps[:5]) + ('...' if len(cluster_peps) > 5 else '')
    })

rep_df = pd.DataFrame(representatives)
rep_df.to_csv('pp220_regional_representatives.csv', index=False)

print(f"\nPP220 regional representatives: {len(rep_df)}")
print("\nFirst 10 regional representatives:")
print(rep_df.head(10))

# Show clusters with multiple peptides
multi = rep_df[rep_df['Cluster_Size'] > 1]
print(f"\nClusters with multiple peptides: {len(multi)}")
if len(multi) > 0:
    print(multi[['Representative', 'Cluster_Size', 'Members']].head(10))
