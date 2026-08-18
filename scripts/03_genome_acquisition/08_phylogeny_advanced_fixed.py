#!/usr/bin/env python3
"""
Section 3.3.4: Phylogeny (Fixed)
Uses conda-installed tools
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_trimal(input_file, output_file):
    """Run trimAl"""
    try:
        cmd = f"trimal -in {input_file} -out {output_file} -automated1"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"✅ trimAl completed")
        return True
    except Exception as e:
        logger.error(f"trimAl failed: {e}")
        return False

def run_iqtree(input_file, output_prefix):
    """Run IQ-TREE with bootstrap"""
    try:
        cmd = f"iqtree2 -s {input_file} -m MFP -B 1000 -nt AUTO -pre {output_prefix}"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"✅ IQ-TREE completed")
        return True
    except Exception as e:
        logger.error(f"IQ-TREE failed: {e}")
        return False

def main():
    align_dir = Path("data/processed/alignments")
    input_file = align_dir / "b646l_aligned.fasta"
    output_file = align_dir / "b646l_trimmed.fasta"
    output_prefix = align_dir / "b646l_phylogeny_bs"
    
    # 1. Run trimAl
    if run_trimal(input_file, output_file):
        logger.info(f"Trimmed: {output_file}")
    else:
        logger.warning("trimAl failed, using original alignment")
        output_file = input_file
    
    # 2. Run IQ-TREE
    run_iqtree(output_file, output_prefix)

if __name__ == "__main__":
    main()
