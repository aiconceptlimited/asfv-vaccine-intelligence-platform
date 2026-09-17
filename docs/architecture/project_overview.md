# ASFV Vaccine Design Platform - Project Overview

## Research Proposal Alignment

This project implements a computational framework for multi-epitope vaccine design against African Swine Fever Virus (ASFV) using East African isolates, following the methodology described in the research proposal.

## Six Analytical Layers

1. ASFV genome and protein curation
2. Comparative sequence and conservation analysis
3. Pig-specific SLA-I and SLA-II epitope prediction
4. Safety, immunogenicity, and machine-learning refinement
5. Multi-objective candidate and construct optimization
6. Structural analysis and experimental-translation design

## Directory Structure

The project follows the data organization specified in Section 3.2.3:

- data/raw/     Unchanged downloaded records
- data/metadata/ Isolate and database metadata
- data/interim/  Extracted and standardized sequences
- data/processed/ Alignments, predictions, filtered results
- results/       Final tables, figures, structures, sequences
- workflow/      Snakemake rules and configuration
- logs/          Software execution records
- dashboard/     Database and visualization application
