# ASFV Vaccine Construct Selection - Final Reproducibility Record

## 1. Architecture Generation
- **Total architectures:** 25,920
- **Epitopes:** 3 CTL + 3 HTL + 6 B-cell
- **Linkers:** AAY (CTL), GPGPG (HTL), GGS (B-cell)
- **QC:** All 203 aa, all epitopes intact

## 2. SLA-I Screening
- **Tool:** NetMHCpan 4.1b
- **Alleles:** SLA-1:0101, SLA-1:0401, SLA-1:1201, SLA-2:0401, SLA-3:0301, SLA-3:0401
- **Metric:** %Rank_EL
- **Threshold:** <0.5% hard exclusion
- **Survivors:** 4,800 architectures

## 3. SLA-II Screening
- **Tool:** MixMHC2pred v2.0.2 (web application)
- **Allele:** SLA_DRA_01_01_02__DRB1_02_02
- **Metric:** %Rank_best
- **Peptides processed:** 294

## 4. Candidate Ranking
- **SLA-I Burden:** (penalty_0.5_1 × 10) + (penalty_1_2 × 3) + num_strong_0.5
- **SLA-II Strong:** %Rank < 2.0
- **SLA-II Weak:** %Rank 2.0-10.0

## 5. Selected Candidate: C05_H06_B241
- **SLA-I Burden:** 13
- **SLA-I Min %Rank:** 0.8314
- **SLA-II Strong:** 1 (MEVLHELEAAAKKEE)
- **SLA-II Weak:** 5
- **Length:** 203 aa

## 6. QC Gates Passed
- [x] SLA-I Burden Definition
- [x] SLA-II Interpretation
- [x] MixMHC2pred Allele Definition
- [x] Overlapping Peptide Collapse
- [x] Individual Construct Examination

## 7. Next Steps
- [ ] Structural prediction (AlphaFold)
- [ ] Physicochemical properties
- [ ] Toxicity/Allergenicity screening
- [ ] Experimental validation
