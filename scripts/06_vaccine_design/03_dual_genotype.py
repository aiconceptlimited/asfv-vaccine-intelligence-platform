#!/usr/bin/env python3
"""
Dual-Genotype Cross-Over Validation Framework
"""

import json
import logging
from pathlib import Path
from Bio import SeqIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def categorize_cd2v():
    """Categorize CD2v sequences by length"""
    
    cd2v_file = Path("data/interim/proteins/EP402R_CD2v_sequences.fasta")
    
    if not cd2v_file.exists():
        logger.error("CD2v file not found")
        return None
    
    categories = {
        "full_length_IX": [],
        "variant_length_II": [],
        "truncated": []
    }
    
    for record in SeqIO.parse(cd2v_file, "fasta"):
        accession = record.id.split('_')[0] if '_' in record.id else record.id
        length = len(str(record.seq))
        
        if length >= 380:
            categories["full_length_IX"].append({"accession": accession, "length": length})
        elif length >= 350:
            categories["variant_length_II"].append({"accession": accession, "length": length})
        else:
            categories["truncated"].append({"accession": accession, "length": length})
    
    output_file = Path("data/metadata/cd2v_categories.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(categories, f, indent=2)
    
    logger.info("=" * 60)
    logger.info("CD2v SEQUENCE CATEGORIES")
    logger.info("=" * 60)
    logger.info(f"  Full-length (Genotype IX): {len(categories['full_length_IX'])} sequences")
    for s in categories["full_length_IX"]:
        logger.info(f"    {s['accession']}: {s['length']} aa")
    logger.info(f"  Variant-length (Genotype II): {len(categories['variant_length_II'])} sequences")
    for s in categories["variant_length_II"]:
        logger.info(f"    {s['accession']}: {s['length']} aa")
    logger.info(f"  Truncated: {len(categories['truncated'])} sequences")
    for s in categories["truncated"]:
        logger.info(f"    {s['accession']}: {s['length']} aa")
    
    logger.info(f"\n✅ Categories saved to: {output_file}")
    return categories

if __name__ == "__main__":
    categorize_cd2v()
