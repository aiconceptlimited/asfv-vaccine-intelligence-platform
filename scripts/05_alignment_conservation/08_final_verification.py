#!/usr/bin/env python3
"""
Final verification of all files
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_files():
    """Verify all required files exist and have content"""
    
    files_to_check = {
        "Pig proteome": "data/raw/reference/sus_scrofa_proteome.fasta",
        "BLAST database": "data/raw/reference/sus_scrofa_proteome.phr",
        "ASFV proteins": "data/processed/proteins/ASFV_proteins.fasta",
        "BLAST results": "data/processed/blast/asfv_vs_pig_blast.json",
        "Clustal alignments": "data/processed/alignments/B646L_p72_sequences_clustal.fasta",
        "ENA confirmation": "data/metadata/ena_confirmation.json",
        "Protein extraction metadata": "data/processed/proteins/protein_metadata.json"
    }
    
    results = {}
    all_pass = True
    
    for name, path_str in files_to_check.items():
        path = Path(path_str)
        if path.exists():
            size = path.stat().st_size
            if size > 0:
                results[name] = {"status": "PASS", "size": size, "path": str(path)}
                logger.info(f"✅ {name}: PASS ({size} bytes)")
            else:
                results[name] = {"status": "FAIL", "size": 0, "path": str(path)}
                logger.error(f"❌ {name}: FAIL (empty file)")
                all_pass = False
        else:
            results[name] = {"status": "FAIL", "size": None, "path": str(path)}
            logger.error(f"❌ {name}: FAIL (not found)")
            all_pass = False
    
    # Save verification results
    output_file = Path("data/metadata/final_verification.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Verification results saved to {output_file}")
    
    # Summary
    logger.info("=" * 60)
    logger.info("FINAL STATUS")
    logger.info("=" * 60)
    if all_pass:
        logger.info("✅ ALL FILES PRESENT AND VALID")
    else:
        logger.warning("⚠️  Some files missing or invalid - see details above")
    
    return all_pass

if __name__ == "__main__":
    verify_files()
