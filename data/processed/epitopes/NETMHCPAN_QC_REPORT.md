# NetMHCpan 4.1b QC Report - ASFV Vaccine Study
**Date:** 2026-08-24
**Status:** Validated Intermediate Dataset

## Summary
- **Total predictions:** 16,476 (4,119 × 4 alleles)
- **Unique peptides:** 4,110
- **Peptide length:** 9-mers (100% verified)

## Alleles Analyzed

| Allele | Type | Profile | Predictions | %Rank Status |
|--------|------|---------|-------------|--------------|
| SLA-1*08:05 | Custom | A | 4,119 | -99.900 (unavailable) |
| SLA-2*05:04 | Custom | A | 4,119 | -99.900 (unavailable) |
| SLA-3:0601 | Library | B | 4,119 | Available |
| SLA-3:0502 | Library | C | 4,119 | Available |

## Key Findings

### Custom-MHC Equivalence
- SLA-1*08:05 and SLA-2*05:04 are **biologically distinct sequences** (361 vs 364 aa)
- NetMHCpan 4.1b generated the **same pseudo-sequence** for both:
- Therefore, they represent **one prediction profile** (Profile A)

### Profile Distribution
- **Profile A (SLA-1/2):** 4,110 unique peptides
- **Profile B (SLA-3:0601):** 4,110 unique peptides
- **Profile C (SLA-3:0502):** 4,110 unique peptides

### Affinity Statistics (<1000 nM threshold)

| Profile | Peptides <1000 nM | Best Affinity |
|---------|------------------|---------------|
| A (SLA-1/2) | 12 | 309 nM (YMRPSTQPL) |
| B (SLA-3:0601) | 6 | 396 nM (MMNQTNYSI) |
| C (SLA-3:0502) | 1 | 973 nM (SNMGISFPL) |

### Tiered Candidates

| Tier | Description | Count |
|------|-------------|-------|
| 1 | Strong multi-profile (<1000 nM in all 3) | **0** |
| 2 | Good multi-profile (<1000 nM in 2) | **0** |
| 3 | Intermediate balance | **1** (RQMVPMSPL) |
| 4 | Single strong profile | **18** |
| 5 | Weak/no strong profile | **4,100** |

### Provisional Candidates (Tiers 3-4)
| Peptide | Protein | Profile A | Profile B | Profile C |
|---------|---------|-----------|-----------|-----------|
| **RQMVPMSPL** | pp220_pep779 | 717 | 1,143 | 1,699 |
| YMRPSTQPL | CD2v_pep287 | 309 | 5,382 | 2,591 |
| SAMEVLHEL | pp220_pep1770 | 517 | 6,165 | 3,015 |
| MMNQTNYSI | pp220_pep1032 | 379 | 10,830 | 2,512 |
| SNMGISFPL | pCP312R_pep262 | 4,563 | 2,214 | 973 |
| RAREFYISW | p72_pep602 | 14,847 | 905 | 9,992 |

## Next Steps (Pending Proposal Criteria)
1. Apply defined binding threshold
2. Integrate conservation data
3. Apply protein/epitope filters
4. Final epitope selection

## Files Archived
- All raw NetMHCpan outputs (36 files)
- Combined datasets for all alleles
- Three-profile ranking matrix
- Tier analysis results

**Location:** ~/asfv_vaccine_platform/data/processed/epitopes/results_archive_20260824/
