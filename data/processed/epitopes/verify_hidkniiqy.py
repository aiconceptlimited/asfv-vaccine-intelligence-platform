print("=" * 80)
print("VERIFY HIDKNIIQY TIER A EVIDENCE")
print("=" * 80)

print("""
=== PEPTIDE: HIDKNIIQY ===
Protein: pp220
Position: 1362-1370
Claimed evidence: Direct pig T-cell evidence (Tier A)

=== VERIFICATION STEPS ===
1. Search IEDB for peptide: HIDKNIIQY
   URL: https://tools.iedb.org/query/
   Search: 'HIDKNIIQY' AND 'pig'

2. Check publication: Bosch-Camós et al., 2021
   PMID: 33430316
   Journal: Vaccines (Basel)

3. Verify exact sequence match
4. Confirm assay type (ELISPOT, IFN-γ)
5. Record PMID and experimental details

=== EXPECTED FINDINGS ===
If verified:
  - IEDB record exists
  - Publication confirms peptide sequence
  - Assay type: ELISPOT/IFN-γ
  - Host: Sus scrofa

If not verified:
  - Downgrade to Tier B (computational evidence)
  - Document as limitation

=== ACTION ===
1. Go to IEDB Query: https://tools.iedb.org/query/
2. Search: 'HIDKNIIQY' AND 'pig'
3. Record findings
4. Report back
""")
