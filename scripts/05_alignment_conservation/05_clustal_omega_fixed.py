#!/usr/bin/env python3
"""
Section 3.5.1: Clustal Omega (FIXED)
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_clustal_omega():
    """Run Clustal Omega on all protein alignments"""
    
    input_dir = Path("data/interim/proteins")
    output_dir = Path("data/processed/alignments")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all protein FASTA files
    fasta_files = list(input_dir.glob("*_sequences.fasta"))
    
    if not fasta_files:
        logger.error("No protein files found")
        return False
    
    for input_file in fasta_files:
        output_file = output_dir / f"{input_file.stem}_clustal.fasta"
        
        logger.info(f"Aligning: {input_file.name}")
        
        try:
            cmd = f"clustalo -i {input_file} -o {output_file} --force --threads 4 --outfmt=fasta"
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            logger.info(f"  ✅ {output_file.name}")
        except Exception as e:
            logger.error(f"  ❌ Failed: {e}")
    
    return True

if __name__ == "__main__":
    run_clustal_omega()
