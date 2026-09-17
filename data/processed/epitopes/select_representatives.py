#!/usr/bin/env python3
import pandas as pd
import re

# Load the combined dataset
df = pd.read_csv('ctl_candidates_combined.csv')

# Clean data
df = df[df['Protein'] != 'Protein']
df = df[df['Peptide'] != 'Peptide']
df = df.dropna(subset=['Peptide'])
df = df.reset_index(drop=True)

print(f"Loaded {len(df)} peptides")

# Load clusters from previous run
# Since we don't have the cluster file, we'll recreate clusters
# and select representatives

peptides = [str(p).strip() for p in df['Peptide'].tolist()]
protein_map = dict(zip(df['Peptide'], df['Protein']))
conservation_map = dict(zip(df['Peptide'], df['Conservation']))
allele_count_map = dict(zip(df['Peptide'], df['Allele_Count']))
alleles_map = dict(zip(df['Peptide'], df['Alleles']))

def calculate_overlap(seq1, seq2):
    """Calculate maximum overlap between two sequences"""
    seq1, seq2 = str(seq1), str(seq2)
    max_overlap = 0
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
            overlap = calculate_overlap(peptide, other)
            if overlap >= min_overlap:
                cluster.append(j)
                used.add(j)
        
        clusters.append(cluster)
    
    return clusters

# Find clusters
clusters = find_clusters(peptides, min_overlap=8)

print(f"Total clusters: {len(clusters)}")

# Select representatives
representatives = []
for idx, cluster in enumerate(clusters):
    cluster_peptides = [peptides[i] for i in cluster]
    
    # Score each peptide in cluster
    best_peptide = None
    best_score = -1
    
    for pep in cluster_peptides:
        # Get metrics
        allele_count = int(allele_count_map.get(pep, 0))
        cons = conservation_map.get(pep, 'N/A')
        
        # Parse conservation score
        if cons != 'N/A' and '/' in cons:
            num, den = cons.split('/')
            cons_score = int(num) / int(den) if int(den) > 0 else 0
        else:
            cons_score = 0
        
        # Combined score: allele_count * 10 + conservation_score * 5
        score = (allele_count * 10) + (cons_score * 5)
        
        if score > best_score:
            best_score = score
            best_peptide = pep
    
    if best_peptide:
        representatives.append({
            'Cluster_ID': f'CL_{idx+1:03d}',
            'Protein': protein_map.get(best_peptide, 'unknown'),
            'Peptide': best_peptide,
            'Conservation': conservation_map.get(best_peptide, 'N/A'),
            'Allele_Count': allele_count_map.get(best_peptide, 0),
            'Alleles': alleles_map.get(best_peptide, ''),
            'Cluster_Size': len(cluster)
        })

# Create DataFrame
rep_df = pd.DataFrame(representatives)

# Sort by Allele_Count descending, then by Conservation
rep_df = rep_df.sort_values(['Allele_Count', 'Cluster_Size'], ascending=[False, False])

# Save
rep_df.to_csv('ctl_cluster_representatives.csv', index=False)

print(f"\nTotal representatives: {len(rep_df)}")
print(f"\nTop 20 representatives (by allele coverage):")
print(rep_df[['Cluster_ID', 'Protein', 'Peptide', 'Allele_Count', 'Conservation']].head(20))

# Summary
print(f"\nAllele coverage distribution among representatives:")
print(rep_df['Allele_Count'].value_counts().sort_index())

print(f"\nProtein distribution:")
print(rep_df['Protein'].value_counts())
