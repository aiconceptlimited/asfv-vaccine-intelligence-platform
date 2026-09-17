# SLA-II (HTL) Methodology Verification

## Original HTL Selection - What We Know

### Tool
- **Name:** MixMHC2pred
- **Version:** vpan_v29 (confirmed from error message)
- **Installation:** Local installation at ~/asfv_vaccine_platform/MixMHC2pred/

### Allele
- **Primary allele:** SLA_DRB1_02_02
- **Format in PWM file:** SLA_DRA_01_01__DRB1_02_02
- **Evidence:** SourceFile column in htl_audit_master_clean.csv shows "cd2v_SLA_DRB1_02_02.xls.xlsx"

### Input Format (NEEDS VERIFICATION)
- **Format:** peptide + 12-aa context (confirmed by error message)
- **Question:** Did the original HTL analysis use context?
- **Question:** What was the exact context format?

### Output Format
- **Columns:** Protein, SourceFile, Pos, ContPos, Peptide, nM, Score, Ave, NB
- **Metric:** nM (IC50) and Score (MixMHC2pred score)
- **Threshold:** Need to verify from original selection

### Selected HTL Epitopes (from htl_final_panel.csv)
1. IVLIYLFSSRKKKAA - 18.29 nM
2. RFIINIRSFKTVMTY - 23.00 nM  
3. KRVRFSLIRVHKTQV - 30.48 nM
4. KEEVRLMVIKLLKKK - 90.95 nM

## What We Need to Verify

1. **Input format:** Did original use 15-mer peptides or full context?
2. **Selection threshold:** What nM cutoff was used for selection?
3. **Score metric:** Was Score or nM used as primary metric?
4. **Context length:** If context was used, was it exactly 12 amino acids?

## Action Items
- [ ] Find original MixMHC2pred input file
- [ ] Find original MixMHC2pred output file
- [ ] Verify threshold from original selection
- [ ] Confirm context format
