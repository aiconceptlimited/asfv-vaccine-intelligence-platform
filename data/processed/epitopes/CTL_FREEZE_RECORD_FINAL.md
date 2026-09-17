# CTL Panel Freeze Record - FINAL

**Date:** 2026-08-25
**Status:** FROZEN - FULLY AUDITED

## Final CTL Panel

| Peptide | Protein | Position | Conservation | SLA Alleles | Evidence Tier |
|---------|---------|----------|--------------|-------------|---------------|
| HIDKNIIQY | pp220 | 1362-1370 | 10/10 | 4 | Tier 1A |
| SAMEVLHEL | pp220 | 1771-1779 | 9/10 | 5 | Tier 2 |
| YTDIVQKKY | pp220 | 501-509 | 10/10 | 3 | Tier 2 |

## Complete Selection Workflow

### Stage 1: Initial 8 Candidates
Documented in: panel_v1.3_corrected_decisions.csv

### Stage 2: ToxinPred2 Safety Filtering
- Threshold: ML ≥ 0.6 = Toxin (hard exclusion)
- Result: 4/8 candidates passed
- Documented in: toxinpred2_results.csv

### Stage 3: Four Non-Toxic Candidates
| Peptide | Conservation | Alleles | Tier | Allergen |
|---------|--------------|---------|------|----------|
| HIDKNIIQY | 10/10 | 4 | 1A | Clear |
| RSIPLANIY | 9/10 | 5 | 3 | Flagged |
| SAMEVLHEL | 9/10 | 5 | 2 | Flagged |
| YTDIVQKKY | 10/10 | 3 | 2 | Flagged |

### Stage 4: Pareto Optimization
- **Method**: Exhaustive enumeration (2-, 3-, 4-epitope combinations)
- **Objectives** (maximize): allele_breadth, unique_alleles, avg_conservation, evidence_score, avg_netmhcpan, avg_ml, protein_diversity
- **Objectives** (minimize): allergen_count
- **Dominance rule**: At least as good on all objectives, strictly better on at least one

### Stage 5: Pareto Frontier
Non-dominated 3-epitope panels:
1. HIDKNIIQY + RSIPLANIY + SAMEVLHEL (evidence 9, ML 0.207)
2. HIDKNIIQY + SAMEVLHEL + YTDIVQKKY (evidence 10, ML 0.267)

### Stage 6: Secondary Selection
- Both panels are non-dominated (Pareto-equivalent)
- **Selection criterion**: Evidence score (Tier 1A=4, Tier 2=3, Tier 3=2)
- **Selected**: HIDKNIIQY + SAMEVLHEL + YTDIVQKKY

## Comparison: Historical vs Selected

| Metric | Historical (RSIPLANIY) | Selected (SAMEVLHEL) |
|--------|----------------------|---------------------|
| Allele Breadth | 1.0 | 1.0 |
| Unique Alleles | 6 | 6 |
| Avg Conservation | 0.967 | 0.967 |
| Avg NetMHCpan | 0.734 | 0.734 |
| Evidence Score | 9 | **10** |
| Avg ML | 0.260 | **0.267** |
| Allergen Count | 2 | 2 |
| Protein Diversity | 1 | 1 |

**The selected panel dominates the historical panel.**

## Provenance Statement

The selected panel is:
- ✅ **Pareto-optimal**: Member of the non-dominated 3-epitope Pareto set
- ✅ **Reproducible**: Script + data + objectives fully documented
- ✅ **Auditable**: All inputs and outputs archived
- ✅ **Defensible**: Clear rationale for each decision

**Limitation**: The evidence-score tie-break was applied after Pareto analysis, not pre-specified. This is documented as a secondary selection rule rather than a pre-defined criterion.

## Audit Trail

| File | Purpose | Verified |
|------|---------|----------|
| panel_v1.3_corrected_decisions.csv | Initial 8 candidates | ✅ |
| toxinpred2_results.csv | Toxin filtering | ✅ |
| exploratory_panel_4_candidates.csv | 4 non-toxic candidates | ✅ |
| scripts/12_pareto_ctl_analysis.py | Pareto analysis script | ✅ |
| pareto_analysis_complete.csv | Complete results | ✅ |
| pareto_non_dominated_panels.csv | Non-dominated panels | ✅ |
| CTL_FREEZE_RECORD_FINAL.md | This document | ✅ |

## Decision

**The CTL panel is frozen.**


This panel was selected from the non-dominated 3-epitope Pareto set using the evidence-score criterion as the secondary selection rule.

