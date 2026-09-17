import pandas as pd
import os
import glob

def audit_file(filepath):
    print(f"\n{'='*60}")
    print(f"FILE: {os.path.basename(filepath)}")
    print(f"PATH: {filepath}")
    print('='*60)
    
    df = pd.read_excel(filepath, header=None)
    
    # Header row
    headers = df.iloc[0].tolist()
    print(f"\nHEADERS: {headers}")
    
    # Data rows
    data = df.iloc[1:]
    print(f"\nTOTAL ROWS: {len(data)}")
    print(f"COLUMNS: {len(df.columns)}")
    
    # Find peptide column
    peptide_col = None
    for i, h in enumerate(headers):
        if h and 'Peptide' in str(h):
            peptide_col = i
            break
    
    if peptide_col is not None:
        peptides = data.iloc[:, peptide_col].dropna().tolist()
        print(f"\nPEPTIDES FOUND: {len(peptides)}")
        if peptides:
            print(f"First peptide: {peptides[0]}")
            print(f"Last peptide: {peptides[-1]}")
            print(f"Peptide length: {len(str(peptides[0]))}")
            
            # Check all are 15-mers
            lengths = [len(str(p)) for p in peptides if p]
            unique_lengths = set(lengths)
            print(f"Unique lengths: {unique_lengths}")
            if len(unique_lengths) == 1 and 15 in unique_lengths:
                print("✅ All peptides are 15-mers")
            else:
                print(f"⚠️ Mixed lengths: {unique_lengths}")
    
    # Find affinity column
    affinity_col = None
    for i, h in enumerate(headers):
        if h and ('nM' in str(h) or 'affinity' in str(h).lower()):
            affinity_col = i
            print(f"\nAFFINITY COLUMN: index {i}, header '{h}'")
            break
    
    print("\n" + "="*60)

# Audit all files
base_dir = os.path.expanduser('~/asfv_vaccine_platform/data/processed/epitopes')
files = glob.glob(os.path.join(base_dir, '**/htl/raw/*.xlsx'), recursive=True)

for f in sorted(files):
    try:
        audit_file(f)
    except Exception as e:
        print(f"ERROR with {f}: {e}")

print(f"\nTotal files audited: {len(files)}")
