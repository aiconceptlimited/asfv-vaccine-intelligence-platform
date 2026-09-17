# SLA Reference Panel - Tier Curation Plan

## Current Status
- All 523 alleles are assigned Tier 3 (default)
- No literature-based tier assignments have been applied

## Curation Process

### Tier 1: Experimentally Validated Alleles
Criteria:
- Published experimental validation of SLA binding
- Known immunogenic peptides
- Evidence of functional SLA presentation

Sources to check:
- IPD-MHC database (experimental evidence field)
- PubMed: "SLA allele peptide binding"
- PubMed: "SLA restriction ASFV"

### Tier 2: African/East African Alleles
Criteria:
- Reported in African pig populations
- Peer-reviewed literature evidence
- Frequency data available

Sources to check:
- PubMed: "SLA African pig"
- PubMed: "indigenous pig SLA"
- IPD-MHC (population data)

### Tier 3: All Other Alleles
Default assignment for alleles without specific evidence

## How to Update
1. Search literature for each allele
2. Update tier field in sla_tier_assignments_full.json
3. Re-run pipeline
4. Document changes
