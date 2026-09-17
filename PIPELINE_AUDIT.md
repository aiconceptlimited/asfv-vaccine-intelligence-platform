# ASFV Vaccine Platform - Pipeline Audit

## 1. Original Epitope Selection (Completed)

### SLA-I (CTL) Selection
- **Tool:** NetMHCpan 4.1b
- **Alleles:** [TO BE VERIFIED]
- **Metric:** %Rank
- **Strong binder:** < 2.0%
- **Weak binder:** < 10.0%
- **Selected epitopes:** 
  - RVFSRLVFY (Tier 1A)
  - HIDKNIIQY (Tier 1A)
  - YTDIVQKKY (Tier 2, IC50 53 nM)
  - [Others]

### SLA-II (HTL) Selection
- **Tool:** [TO BE VERIFIED - appears to be NetMHCIIpan]
- **Allele:** SLA_DRB1_02_02
- **Metric:** nM
- **Threshold:** [TO BE VERIFIED]
- **Selected epitopes:**
  - IVLIYLFSSRKKKAA (18.29 nM)
  - RFIINIRSFKTVMTY (23.00 nM)
  - KRVRFSLIRVHKTQV (30.48 nM)
  - KEEVRLMVIKLLKKK (90.95 nM)

## 2. Architecture Enumeration (Completed)
- **Number:** 25,920 architectures
- **Epitopes:** 12 frozen
- **Linkers:** AAY (CTL), GPGPG (HTL), GGS (B-cell)
- **QC:** All 203 aa, all epitopes intact

## 3. Junction Extraction (Completed)
- **Total junctions:** 2,928,960
- **Unique SLA-I peptides:** 494
- **Unique SLA-II peptides:** 294
- **Mapping:** Need to verify peptide → architecture mapping

## 4. Junction Screening (Pending)
### SLA-I Junctions
- **Tool:** NetMHCpan 4.1b
- **Alleles:** [Same as original]
- **Input:** 494 unique peptides
- **Total predictions:** 494 × 6 = 2,964
- **Purpose:** Identify unintended SLA-I binders at junctions

### SLA-II Junctions
- **Tool:** [Same as original - NetMHCIIpan]
- **Allele:** SLA_DRB1_02_02
- **Input:** 294 unique 15-mer peptides
- **Total predictions:** 294 × 1 = 294
- **Purpose:** Identify unintended SLA-II binders at junctions

## 5. Filtering and Ranking (Pending)
- **Filter:** Remove architectures with strong binder junctions
- **Rank:** By epitope coverage
- **Selection:** Top 10-20 candidates

## 6. Action Items
- [ ] Verify SLA-I alleles from original analysis
- [ ] Verify SLA-II predictor from original analysis
- [ ] Verify original thresholds
- [ ] Verify peptide → architecture mapping
- [ ] Confirm junction screening methodology matches original
- [ ] Run junction screens with consistent methodology
- [ ] Map results back to architectures
- [ ] Filter and rank candidates
