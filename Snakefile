# Snakefile
# ASFV Vaccine Design Pipeline - Master Workflow
# Following Section 3.2.1 of the proposal
# Only includes rules for implemented sections

configfile: "config/pipeline.yaml"

# Include workflow rules (only those that exist)
include: "workflow/rules/03_genome_acquisition.smk"
include: "workflow/rules/04_protein_extraction.smk"

# Additional rules will be added as sections are implemented
# include: "workflow/rules/05_alignment.smk"
# include: "workflow/rules/06_sla_reference.smk"
# include: "workflow/rules/07_epitope_prediction.smk"
# include: "workflow/rules/08_screening.smk"
# include: "workflow/rules/09_ml_refinement.smk"
# include: "workflow/rules/10_population_coverage.smk"
# include: "workflow/rules/11_optimization.smk"
# include: "workflow/rules/12_construct_design.smk"
# include: "workflow/rules/13_adjuvant.smk"
# include: "workflow/rules/14_characterization.smk"
# include: "workflow/rules/15_structure_prediction.smk"
# include: "workflow/rules/16_peptide_sla.smk"
# include: "workflow/rules/17_tlr.smk"
# include: "workflow/rules/18_molecular_dynamics.smk"
# include: "workflow/rules/19_codon_optimization.smk"
# include: "workflow/rules/20_cloning.smk"
# include: "workflow/rules/21_dashboard.smk"

rule all:
    input:
        "results/final/pipeline_complete.txt"

rule pipeline_complete:
    output:
        "results/final/pipeline_complete.txt"
    shell:
        "echo 'Pipeline completed on $(date)' > {output}"
