#!/usr/bin/env python3
import pandas as pd
import re

# Load combined candidates
df = pd.read_csv('ctl_candidates_combined.csv')

# Remove the header row if present
df = df[df['Protein'] != 'Protein']

def find_overlaps(peptides, min_overlap=8):
    """Group overlapping 9-mer peptides"""
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
            # Check overlap between peptide sequences
            seq1 = peptide.split('|')[1] if '|' in peptide else peptide
            seq2 = other.split('|')[1] if '|' in other else other
            
            max_overlap = 0
            for shift in range(1, min(len(seq1), len(seq2))):
                if seq1[-shift:] == seq2[:shift]:
                    max_overlap = max(max_overlap, shift)
                if seq2[-shift:] == seq1[:shift]:
                    max_overlap = max(max_overlap, shift)
            
            if max_overlap >= min_overlap:
                cluster.append(j)
                used.add(j)
        
        if len(cluster) > 1:
            clusters.append(cluster)
        else:
            clusters.append(cluster)  # Keep singletons
    
    return clusters

# Convert to list of peptides with protein info
peptides = df['Peptide'].tolist()
protein_map = dict(zip(df['Peptide'], df['Protein']))

# Find clusters
clusters = find_overlaps(peptides, min_overlap=8)

# Create summary
cluster_summary = []
for idx, cluster in enumerate(clusters):
    cluster_peptides = [peptides[i] for i in cluster]
    cluster_proteins = [protein_map[p] for p in cluster_peptides]
    cluster_summary.append({
        'Cluster_ID': f'CL_{idx+1:03d}',
        'Size': len(cluster),
        'Proteins': ';'.join(set(cluster_proteins)),
        'Peptides': ';'.join(cluster_peptides)
    })

cluster_df = pd.DataFrame(cluster_summary)
cluster_df.to_csv('ctl_clusters.csv', index=False)

print(f"Total clusters: {len(cluster_df)}")
print(f"Clusters with >1 peptide: {len(cluster_df[cluster_df['Size'] > 1])}")
print(f"Singleton clusters: {len(cluster_df[cluster_df['Size'] == 1])}")
print("\nCluster distribution:")
print(cluster_df['Size'].value_counts().sort_index())

# Show first 10 clusters
print("\nFirst 10 clusters:")
print(cluster_df.head(10))
