#!/usr/bin/env python3
"""Section 3.5.1: Clustal Omega Comparison"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_clustal_omega(input_file, output_file):
    try:
        cmd = f"clustalo -i {input_file} -o {output_file} --force --threads 4"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        return True
    except Exception as e:
        logger.error(f"Clustal Omega failed: {e}")
        return False

def main():
    output_dir = Path("data/processed/alignments")
    for fasta in Path("data/interim/proteins").glob("*.fasta"):
        gene = fasta.stem.split('_')[0]
        protein = fasta.stem.split('_')[1] if '_' in fasta.stem else 'unknown'
        output_file = output_dir / f"{gene}_{protein}_clustal.fasta"
        
        if run_clustal_omega(fasta, output_file):
            logger.info(f"✅ {gene}_{protein}: Clustal Omega complete")

if __name__ == "__main__":
    main()
