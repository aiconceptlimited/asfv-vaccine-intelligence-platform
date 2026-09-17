#!/usr/bin/env python3
import pandas as pd

# Load combined candidates
df = pd.read_csv('ctl_candidates_combined.csv')

# Clean data
df = df[df['Protein'] != 'Protein']
df = df[df['Peptide'] != 'Peptide']
df = df.dropna(subset=['Peptide'])

print(f"Loaded {len(df)} peptides")

if len(df) == 0:
    print("No peptides loaded. Check input file.")
    exit()

# Get peptide list
peptides = [str(p).strip() for p in df['Peptide'].tolist()]
protein_map = dict(zip(df['Peptide'], df['Protein']))

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

# Build cluster summary
cluster_data = []
for idx, cluster in enumerate(clusters):
    cluster_peptides = [peptides[i] for i in cluster]
    cluster_proteins = set()
    for p in cluster_peptides:
        if p in protein_map:
            cluster_proteins.add(protein_map[p])
    
    cluster_data.append({
        'Cluster_ID': f'CL_{idx+1:03d}',
        'Size': len(cluster),
        'Proteins': ';'.join(sorted(cluster_proteins)) if cluster_proteins else 'unknown',
        'Peptides': ';'.join(cluster_peptides[:5]) + ('...' if len(cluster_peptides) > 5 else '')
    })

cluster_df = pd.DataFrame(cluster_data)
cluster_df.to_csv('ctl_clusters_final.csv', index=False)

print(f"Clusters with >1 peptide: {len([c for c in cluster_data if c['Size'] > 1])}")
print(f"Singleton clusters: {len([c for c in cluster_data if c['Size'] == 1])}")

if len(cluster_data) > 0:
    print("\nCluster distribution:")
    size_counts = {}
    for c in cluster_data:
        size_counts[c['Size']] = size_counts.get(c['Size'], 0) + 1
    for size in sorted(size_counts.keys()):
        print(f"  Size {size}: {size_counts[size]} clusters")
    
    print("\nFirst 10 clusters:")
    for c in cluster_data[:10]:
        print(f"  {c['Cluster_ID']}: Size {c['Size']}, Proteins: {c['Proteins']}")
