#!/usr/bin/env python3
"""
Extract N-terminal 159 amino acids from CD2v sequences
"""

import logging
from pathlib import Path
from Bio import SeqIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_nt159():
    """Extract first 159 aa from all CD2v sequences"""
    
    input_file = Path("data/interim/proteins/EP402R_CD2v_sequences.fasta")
    output_file = Path("data/interim/proteins/EP402R_CD2v_Nterminal_159aa.fasta")
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return False
    
    records = []
    for record in SeqIO.parse(input_file, "fasta"):
        seq = str(record.seq)
        accession = record.id.split('_')[0] if '_' in record.id else record.id
        
        if len(seq) >= 159:
            trimmed_seq = seq[:159]
            record.seq = trimmed_seq
            record.description = f"{record.description}|Nterminal_159aa"
            records.append(record)
            logger.info(f"  {accession}: {len(seq)} aa → 159 aa")
        else:
            # Keep shorter sequences as-is
            record.description = f"{record.description}|SHORT_{len(seq)}aa"
            records.append(record)
            logger.info(f"  {accession}: {len(seq)} aa (already short)")
    
    with open(output_file, "w") as f:
        SeqIO.write(records, f, "fasta")
    
    logger.info(f"✅ N-terminal 159 aa saved to: {output_file}")
    return True

if __name__ == "__main__":
    extract_nt159()
