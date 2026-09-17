#!/usr/bin/env python3
import pandas as pd
import re

# Load combined candidates
df = pd.read_csv('ctl_candidates_combined.csv')

# Remove any header rows if present
df = df[df['Protein'] != 'Protein']
df = df[df['Peptide'] != 'Peptide']

# Drop rows with missing peptides
df = df.dropna(subset=['Peptide'])

print(f"Loaded {len(df)} peptides")

# Get peptide list (ensure they are strings)
peptides = [str(p).strip() for p in df['Peptide'].tolist()]
protein_map = dict(zip(df['Peptide'], df['Protein']))

def calculate_overlap(seq1, seq2):
    """Calculate maximum overlap between two sequences"""
    max_overlap = 0
    seq1, seq2 = str(seq1), str(seq2)
    for shift in range(1, min(len(seq1), len(seq2))):
        if seq1[-shift:] == seq2[:shift]:
            max_overlap = max(max_overlap, shift)
        if seq2[-shift:] == seq1[:shift]:
            max_overlap = max(max_overlap, shift)
    return max_overlap

def find_clusters(peptides, min_overlap=8):
    """Group overlapping peptides into clusters"""
    clusters = []
    used = set()
    
    for i, peptide in enumerate(peptides):
        if i in used:
            continue
        cluster = [i]
        used.add(i)
        
        for j, other in enumerate(peptides):
            if j in used:
                continue
            # Calculate overlap
            overlap = calculate_overlap(peptide, other)
            if overlap >= min_overlap:
                cluster.append(j)
                used.add(j)
        
        # Store cluster even if singleton (for completeness)
        clusters.append(cluster)
    
    return clusters

# Find clusters
clusters = find_clusters(peptides, min_overlap=8)

print(f"Total clusters: {len(clusters)}")

# Create cluster summary
cluster_data = []
for idx, cluster in enumerate(clusters):
    cluster_peptides = [peptides[i] for i in cluster]
    cluster_proteins = set()
    for p in cluster_peptides:
        for protein, peptide in protein_map.items():
            if peptide == p:
                cluster_proteins.add(protein)
    
    cluster_data.append({
        'Cluster_ID': f'CL_{idx+1:03d}',
        'Size': len(cluster),
        'Proteins': ';'.join(sorted(cluster_proteins)) if cluster_proteins else 'unknown',
        'Peptides': ';'.join(cluster_peptides[:5]) + ('...' if len(cluster_peptides) > 5 else '')
    })

cluster_df = pd.DataFrame(cluster_data)
cluster_df.to_csv('ctl_clusters.csv', index=False)

print(f"Total clusters: {len(cluster_df)}")
print(f"Clusters with >1 peptide: {len(cluster_df[cluster_df['Size'] > 1])}")
print(f"Singleton clusters: {len(cluster_df[cluster_df['Size'] == 1])}")

if len(cluster_df) > 0:
    print("\nCluster distribution:")
    print(cluster_df['Size'].value_counts().sort_index())
    
    print("\nFirst 10 clusters:")
    print(cluster_df[['Cluster_ID', 'Size', 'Proteins']].head(10))
else:
    print("⚠️ No clusters found — check input data")
