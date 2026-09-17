# SLA Reference Panel - ASFV Vaccine Platform

## Overview
This reference panel contains 523 SLA alleles from the IPD-MHC database, curated for use in SLA-aware epitope prediction for ASFV vaccine design.

## Composition

| Category | Count | Loci |
|----------|-------|------|
| Class I | 270 | SLA-1 (108), SLA-2 (105), SLA-3 (47), SLA-6 (10) |
| Class II | 221 | SLA-DRB (116), SLA-DQB1 (55), SLA-DQA (27), SLA-DRA (16), SLA-DMA (7) |
| Other SLA Loci | 32 | SLA-4, SLA-7, SLA-8, SLA-9, TAP1, TAP2, DOB1 |

## Tier Definitions

| Tier | Criteria | Current Status |
|------|----------|----------------|
| **Tier 1** | Experimentally validated SLA alleles with published evidence of peptide binding, tetramer data, crystal structure, or restriction studies | ⏳ Pending curation |
| **Tier 2** | Alleles reported in African or East African pig populations with published frequency data | ⏳ Pending curation |
| **Tier 3** | All remaining alleles (default assignment) | ✅ Assigned to all 523 alleles |

## Tier Curation Strategy

### Tier 1 Criteria
- Published experimental validation of SLA binding
- Known immunogenic peptides
- Evidence of functional SLA presentation
- Sources: IPD-MHC, PubMed, published binding assays

### Tier 2 Criteria
- Reported in African or East African pig populations
- Peer-reviewed literature evidence
- Frequency data available
- Sources: PubMed, population genetics studies

### Tier 3
- Default assignment for alleles without specific evidence

## Usage Guidelines

### For Epitope Prediction (Section 3.7)
- **Primary SLA-I CTL prediction**: Use Class I alleles (270)
- **Primary SLA-II HTL prediction**: Use Class II alleles (221)
- **Other SLA Loci**: Retained for completeness, excluded from primary prediction

## Source
- **Database**: IPD-MHC SLA Database
- **Release**: 2026-04 (requires verification)
- **Download Date**: 2026-08-04
- **URL**: https://www.ebi.ac.uk/ipd/mhc/sla/
- **Total Alleles**: 523

## Files
- `reference_panel_all.fasta`: All 523 alleles
- `reference_panel_class_I.fasta`: 270 Class I alleles
- `reference_panel_class_II.fasta`: 221 Class II alleles
- `reference_panel_metadata.json`: Complete metadata
- `qc_report.json`: Quality control report
- `provenance.json`: Execution provenance with checksums

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-04 | Initial reference panel built from IPD-MHC |

## Next Steps
1. Curate Tier 1 and Tier 2 assignments from literature
2. Update tier file and re-run pipeline
3. Proceed to Section 3.7 (Epitope Prediction)
