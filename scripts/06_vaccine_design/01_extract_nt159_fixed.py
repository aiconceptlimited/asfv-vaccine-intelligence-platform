#!/usr/bin/env python3
"""
Extract N-terminal 159 amino acids from CD2v sequences
FIXED: Properly handles Seq objects
"""

import logging
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

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
        seq_str = str(record.seq)
        accession = record.id.split('_')[0] if '_' in record.id else record.id
        original_len = len(seq_str)
        
        if original_len >= 159:
            # Take first 159 aa and create new SeqRecord
            trimmed_seq = Seq(seq_str[:159])
            new_record = SeqRecord(
                trimmed_seq,
                id=record.id,
                description=f"{record.description}|Nterminal_159aa"
            )
            records.append(new_record)
            logger.info(f"  {accession}: {original_len} aa → 159 aa")
        else:
            # Keep shorter sequences as-is
            new_record = SeqRecord(
                Seq(seq_str),
                id=record.id,
                description=f"{record.description}|SHORT_{original_len}aa"
            )
            records.append(new_record)
            logger.info(f"  {accession}: {original_len} aa (already short)")
    
    with open(output_file, "w") as f:
        SeqIO.write(records, f, "fasta")
    
    logger.info(f"✅ N-terminal 159 aa saved to: {output_file}")
    logger.info(f"📊 Total sequences: {len(records)}")
    return True

if __name__ == "__main__":
    extract_nt159()
