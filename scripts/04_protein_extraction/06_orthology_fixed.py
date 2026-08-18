#!/usr/bin/env python3
"""
Section 3.4.3: Orthology (FIXED)
"""

import subprocess
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_blastp():
    """Run BLASTp against pig proteome"""
    
    query = Path("data/processed/proteins/ASFV_proteins.fasta")
    db = Path("data/raw/reference/sus_scrofa_proteome")
    output = Path("data/processed/blast/asfv_vs_pig_blast.json")
    
    if not query.exists():
        logger.error(f"Query file not found: {query}")
        logger.info("Please run protein extraction first")
        return False
    
    if not Path(str(db) + ".phr").exists():
        logger.error("BLAST database not found")
        logger.info("Please run pig proteome download first")
        return False
    
    output.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        cmd = f"blastp -query {query} -db {db} -out {output} -outfmt 15 -evalue 1e-5 -num_threads 4 -max_target_seqs 1"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"✅ BLASTp completed")
        
        # Parse results
        with open(output, 'r') as f:
            import json as json_lib
            data = json_lib.load(f)
            hits = len(data.get('BlastOutput2', []))
            logger.info(f"📊 Total hits: {hits}")
        
        return True
    except Exception as e:
        logger.error(f"❌ BLASTp failed: {e}")
        return False

if __name__ == "__main__":
    run_blastp()
