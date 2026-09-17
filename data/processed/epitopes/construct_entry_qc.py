#!/usr/bin/env python3
import pandas as pd

# Define combined candidates
candidates = [
    # CTL candidates
    {"Type": "CTL", "Protein": "pp220", "Peptide": "SQWDLVQKF", "Alleles": 6, "Conservation": "10/10", "Position": 1091},
    {"Type": "CTL", "Protein": "pp220", "Peptide": "RVFSRLVFY", "Alleles": 5, "Conservation": "10/10", "Position": 1462},
    {"Type": "CTL", "Protein": "pp220", "Peptide": "HIDKNIIQY", "Alleles": 4, "Conservation": "10/10", "Position": 1362},
    {"Type": "CTL", "Protein": "pp220", "Peptide": "RSIPLANIY", "Alleles": 5, "Conservation": "9/10", "Position": 2008},
    {"Type": "CTL", "Protein": "pp220", "Peptide": "SAMEVLHEL", "Alleles": 5, "Conservation": "9/10", "Position": 1771},
    {"Type": "CTL", "Protein": "p30", "Peptide": "KTLLSTVKY", "Alleles": 4, "Conservation": "10/11", "Position": "TO_VERIFY"},
    {"Type": "CTL", "Protein": "pp220", "Peptide": "DRKHILMEF", "Alleles": 3, "Conservation": "10/10", "Position": 385},
    {"Type": "CTL", "Protein": "pp220", "Peptide": "YTDIVQKKY", "Alleles": 3, "Conservation": "10/10", "Position": 501},
    # HTL candidates
    {"Type": "HTL", "Protein": "p54", "Peptide": "IVLIYLFSSRKKKAA", "Alleles": "HTL", "Conservation": "4/4", "Position": 46},
    {"Type": "HTL", "Protein": "pp220", "Peptide": "RFIINIRSFKTVMTY", "Alleles": "HTL", "Conservation": "3/3", "Position": 1898},
    {"Type": "HTL", "Protein": "p30", "Peptide": "KEEVRLMVIKLLKKK", "Alleles": "HTL", "Conservation": "4/4", "Position": 179},
]

# Create DataFrame
df = pd.DataFrame(candidates)

print("=== CONSTRUCT-ENTRY QC ===")
print(f"Total candidates: {len(df)}")
print(f"CTL candidates: {len(df[df['Type'] == 'CTL'])}")
print(f"HTL candidates: {len(df[df['Type'] == 'HTL'])}")

print("\n=== CANDIDATE SUMMARY ===")
print(df[['Type', 'Protein', 'Peptide', 'Alleles', 'Conservation', 'Position']])

# Check for missing coordinates
missing = df[df['Position'] == 'TO_VERIFY']
if len(missing) > 0:
    print(f"\n⚠️ Missing coordinates: {missing['Peptide'].tolist()}")
else:
    print("\n✅ All coordinates verified")

# Check for duplicates
duplicates = df[df.duplicated(subset=['Peptide'], keep=False)]
if len(duplicates) > 0:
    print(f"\n⚠️ Duplicate peptides: {duplicates['Peptide'].tolist()}")
else:
    print("✅ No duplicate peptides")

# Save
df.to_csv('combined_panel_for_construct.csv', index=False)
print("\n✅ Combined panel saved to combined_panel_for_construct.csv")
