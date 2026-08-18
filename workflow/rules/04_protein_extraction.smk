# 04_protein_extraction.smk
# Section 3.4: Protein Extraction
# Extracts 6 target proteins from GenBank files

rule extract_proteins:
    input:
        genbank = expand("data/raw/genomes/{accession}.genbank",
                         accession = config["genomes"])
    output:
        done = "data/interim/proteins/.extract_complete",
        proteins = expand("data/interim/proteins/{gene}_proteins.fasta",
                          gene = config["target_proteins"])
    log:
        "logs/extract/04_extract.log"
    script:
        "../scripts/04_protein_extraction/02_extract_proteins.py"
