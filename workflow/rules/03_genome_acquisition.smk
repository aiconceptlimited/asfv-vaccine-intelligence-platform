# 03_genome_acquisition.smk
# Section 3.3: Genome Acquisition
# Downloads 11 ASFV genomes from NCBI GenBank

rule download_genomes:
    input:
        manifest = "workflow/resources/accession_manifest.txt"
    output:
        done = "data/raw/genomes/.download_complete",
        report = "data/metadata/download_report.json"
    params:
        email = os.environ.get("NCBI_EMAIL", ""),
        retries = 3
    log:
        "logs/download/03_download.log"
    shell:
        """
        set -euo pipefail
        python scripts/03_genome_acquisition/01_download_genomes.py \
            --email {params.email} \
            --retries {params.retries} \
            2>&1 | tee {log}
        touch {output.done}
        """
