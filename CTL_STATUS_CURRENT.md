# CTL Epitope Selection - Current Status

**Date:** [Current Date]
**Status:** Under Investigation

## Summary

| Metric | Value |
|--------|-------|
| Total CTL candidates identified | 8 |
| Candidate dataset quality | Well supported |
| 8 → 3 reduction reproducibility | ❌ Not established |
| Final 3 status | Provisional |

## The 8 Candidates

| # | Peptide | Conservation | Alleles | Tier | Decision |
|---|---------|--------------|---------|------|----------|
| 1 | SQWDLVQKF | 10/10 | 6 | 2 | KEEP |
| 2 | RVFSRLVFY | 10/10 | 5 | 1A | KEEP |
| 3 | HIDKNIIQY | 10/10 | 4 | 1A | KEEP |
| 4 | RSIPLANIY | 9/10 | 5 | 3 | REVIEW |
| 5 | SAMEVLHEL | 9/10 | 5 | 2 | KEEP |
| 6 | DRKHILMEF | 10/10 | 3 | 2-3 | KEEP |
| 7 | YTDIVQKKY | 10/10 | 3 | 2 | KEEP |
| 8 | KTLLSTVKY | 10/11 | 4 | 3 | REVIEW |

## The Provisional 3

| # | Peptide | Conservation | Alleles | Tier | Status |
|---|---------|--------------|---------|------|--------|
| 1 | HIDKNIIQY | 10/10 | 4 | 1A | Provisional |
| 2 | RSIPLANIY | 9/10 | 5 | 3 | Provisional |
| 3 | YTDIVQKKY | 10/10 | 3 | 2 | Provisional |

## Provenance Gap

The transition from 8 candidates to 3 provisional candidates is not documented.

**Key inconsistencies:**
- 4 KEEP candidates were excluded without clear rationale
- 1 REVIEW candidate (RSIPLANIY) was included
- Allergen-flagged peptides inconsistently handled (SAMEVLHEL excluded, YTDIVQKKY included)

## Next Steps

1. Complete file discovery search
2. Reconstruct selection data lineage
3. Either:
   a. Document the existing selection rule, OR
   b. Rerun the selection transparently

## Recommendation

**Do not freeze the CTL panel** until the 8 → 3 transition is documented and reproducible.

