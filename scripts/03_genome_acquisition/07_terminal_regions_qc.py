#!/usr/bin/env python3
"""
Section 3.3.3: SeqKit + Terminal Regions QC
"""

import json
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_seqkit(fasta_file):
    """Run SeqKit stats"""
    try:
        cmd = f"seqkit stats {fasta_file} -a -T"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"SeqKit failed: {e}")
        return None

def main():
    output_dir = Path("data/metadata/seqkit_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    for fasta in Path("data/raw/genomes").glob("*.fasta"):
        accession = fasta.stem
        logger.info(f"Processing {accession}...")
        output = run_seqkit(fasta)
        if output:
            results[accession] = output
            with open(output_dir / f"{accession}_seqkit.txt", "w") as f:
                f.write(output)
    
    with open(output_dir / "seqkit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {output_dir}/")

if __name__ == "__main__":
    main()
