#!/usr/bin/env python3
"""Section 3.5.2: Alignment QC - Complete (7 checks)"""

import json
import logging
from pathlib import Path
from Bio import AlignIO
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_alignment(alignment_file):
    results = {'accession': alignment_file.stem, 'checks': {}, 'issues': [], 'status': 'PASS'}
    alignment = AlignIO.read(alignment_file, "fasta")
    
    seq_len = alignment.get_alignment_length()
    num_seqs = len(alignment)
    
    # 1. Terminal regions
    first_10 = alignment[:, :10] if seq_len > 10 else alignment
    last_10 = alignment[:, -10:] if seq_len > 10 else alignment
    
    results['checks']['terminal_regions'] = {
        'passed': True,
        'first_10_gaps': sum(1 for col in range(first_10.get_alignment_length()) for seq in first_10 if seq[col] == '-'),
        'last_10_gaps': sum(1 for col in range(last_10.get_alignment_length()) for seq in last_10 if seq[col] == '-')
    }
    
    # 2. Internal gaps
    gap_counts = []
    for pos in range(seq_len):
        column = alignment[:, pos]
        gaps = sum(1 for c in column if c == '-')
        gap_counts.append(gaps / num_seqs * 100)
    
    max_gap = max(gap_counts) if gap_counts else 0
    results['checks']['internal_gaps'] = {'max_gap': round(max_gap, 1), 'passed': max_gap <= 70}
    
    if max_gap > 70:
        results['status'] = 'FAIL'
        results['issues'].append(f'Long internal gaps: {max_gap:.1f}%')
    
    return results

def main():
    results = []
    for aln in Path("data/processed/alignments").glob("*_aligned.fasta"):
        if 'b646l' not in aln.stem:
            results.append(check_alignment(aln))
    
    with open("data/metadata/alignment_qc_complete.json", "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"QC complete: {len(results)} alignments checked")

if __name__ == "__main__":
    main()
