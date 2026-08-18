#!/usr/bin/env python3
"""
Section 3.3.4: Genotype Confirmation - Advanced
Run trimAl and ultrafast bootstrap

Input:  data/processed/alignments/b646l_aligned.fasta
Output: data/processed/alignments/b646l_trimmed.fasta
        data/processed/alignments/b646l_phylogeny_bs/

Author: Abubakar
Date: 2026-07-15
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_trimal(input_file, output_file):
    """Run trimAl for alignment trimming"""
    
    try:
        cmd = f"trimal -in {input_file} -out {output_file} -automated1"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"✅ trimAl completed: {output_file}")
        return True
    except Exception as e:
        logger.error(f"trimAl failed: {e}")
        return False

def run_iqtree_bootstrap(input_file, output_prefix):
    """Run IQ-TREE with ultrafast bootstrap"""
    
    try:
        cmd = f"iqtree2 -s {input_file} -m MFP -B 1000 -nt AUTO -pre {output_prefix}"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"✅ IQ-TREE with bootstrap completed: {output_prefix}")
        return True
    except Exception as e:
        logger.error(f"IQ-TREE failed: {e}")
        return False

def parse_bootstrap_results(output_prefix):
    """Parse bootstrap results"""
    
    treefile = Path(f"{output_prefix}.treefile")
    iqtree = Path(f"{output_prefix}.iqtree")
    
    results = {
        'treefile_exists': treefile.exists(),
        'iqtree_exists': iqtree.exists(),
        'bootstrap_values': []
    }
    
    if iqtree.exists():
        with open(iqtree, 'r') as f:
            content = f.read()
            # Extract bootstrap values
            import re
            values = re.findall(r'(\d+)%', content)
            results['bootstrap_values'] = values[:10]  # First 10 values
    
    return results

def main():
    """Main function"""
    
    logger.info("=" * 60)
    logger.info("Section 3.3.4: trimAl + Ultrafast Bootstrap")
    logger.info("=" * 60)
    
    # Define paths
    alignments_dir = Path("data/processed/alignments")
    input_file = alignments_dir / "b646l_aligned.fasta"
    output_file = alignments_dir / "b646l_trimmed.fasta"
    output_prefix = alignments_dir / "b646l_phylogeny_bs"
    
    # 1. Run trimAl
    logger.info("\n1. Running trimAl...")
    if run_trimal(input_file, output_file):
        logger.info(f"   Trimmed alignment saved to: {output_file}")
        
        # Compare lengths
        with open(input_file, 'r') as f:
            original = len(f.read())
        with open(output_file, 'r') as f:
            trimmed = len(f.read())
        logger.info(f"   Original: {original} characters")
        logger.info(f"   Trimmed: {trimmed} characters")
        logger.info(f"   Removed: {original - trimmed} characters")
    else:
        logger.error("trimAl failed. Using original alignment.")
        output_file = input_file
    
    # 2. Run IQ-TREE with ultrafast bootstrap
    logger.info("\n2. Running IQ-TREE with ultrafast bootstrap...")
    if run_iqtree_bootstrap(output_file, output_prefix):
        results = parse_bootstrap_results(output_prefix)
        logger.info(f"   Treefile: {results['treefile_exists']}")
        logger.info(f"   IQ-TREE report: {results['iqtree_exists']}")
        if results['bootstrap_values']:
            logger.info(f"   Bootstrap values: {', '.join(results['bootstrap_values'][:5])}...")
    else:
        logger.error("IQ-TREE with bootstrap failed")
    
    # 3. Save summary
    summary = {
        'input_file': str(input_file),
        'trimmed_file': str(output_file),
        'bootstrap_prefix': str(output_prefix),
        'trimmed': output_file.exists(),
        'bootstrap_completed': Path(f"{output_prefix}.treefile").exists()
    }
    
    with open(alignments_dir / "phylogeny_advanced_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"\nSummary saved to: {alignments_dir}/phylogeny_advanced_summary.json")

if __name__ == "__main__":
    main()
