import pandas as pd
import re

# Read the file - it has a complex header
with open('netmhcpan_SLA-1_0101.tsv', 'r') as f:
    lines = f.readlines()

# Find the data header line
for i, line in enumerate(lines):
    if line.startswith('Pos\tPeptide\tID'):
        data_start = i
        break

# Read data from that point
df = pd.read_csv('netmhcpan_SLA-1_0101.tsv', 
                 skiprows=data_start,
                 sep='\t',
                 header=0)

# The columns are:
# 0: Pos, 1: Peptide, 2: ID, 
# Then for each allele: core, icore, EL-score, EL_Rank
# All 6 alleles, then Ave, NB

# Extract each allele's data
alleles = ['SLA-1:0101', 'SLA-1:0401', 'SLA-1:1201', 
           'SLA-2:0401', 'SLA-3:0301', 'SLA-3:0401']

# Column positions for each allele (3 + 4*allele_index)
for i, allele in enumerate(alleles):
    base_col = 3 + (i * 4)
    el_score_col = base_col + 2
    el_rank_col = base_col + 3
    
    # Extract peptide and rank
    data = df.iloc[:, [1, el_rank_col, el_score_col]].copy()
    data.columns = ['Peptide', '%Rank_EL', 'Score_EL']
    data['MHC'] = allele
    data['Pos'] = df['Pos']
    
    # Save to file
    filename = f"netmhcpan_{allele.replace(':', '_')}_parsed.tsv"
    data.to_csv(filename, sep='\t', index=False)
    print(f"Created {filename}")

print("\n✅ All files parsed successfully!")
