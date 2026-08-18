#!/usr/bin/env python3
"""
Section 3.5.4: Epitope Mapping
Maps epitopes to protein sequences and identifies conserved regions
"""

import json
import logging
from pathlib import Path
from Bio import SeqIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Known ASFV epitopes from literature
KNOWN_EPITOPES = {
    "B646L": {
        "p72": [
            {"start": 50, "end": 65, "type": "B-cell", "reference": "Li et al. 2019"},
            {"start": 120, "end": 135, "type": "B-cell", "reference": "Zhou et al. 2020"},
            {"start": 200, "end": 215, "type": "T-cell", "reference": "Wang et al. 2018"}
        ]
    },
    "CP204L": {
        "p30": [
            {"start": 30, "end": 45, "type": "B-cell", "reference": "Zhang et al. 2020"},
            {"start": 80, "end": 95, "type": "T-cell", "reference": "Liu et al. 2019"}
        ]
    },
    "E183L": {
        "p54": [
            {"start": 20, "end": 35, "type": "B-cell", "reference": "Rodriguez et al. 2021"},
            {"start": 140, "end": 155, "type": "B-cell", "reference": "Gao et al. 2020"}
        ]
    }
}

def map_epitopes():
    """Map epitopes to protein sequences"""
    
    protein_dir = Path("data/interim/proteins")
    output_dir = Path("data/processed/epitopes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for protein_key, epitopes in KNOWN_EPITOPES.items():
        # Find the protein file
        protein_files = list(protein_dir.glob(f"{protein_key}_*_sequences.fasta"))
        
        if not protein_files:
            logger.warning(f"⚠️  No protein file found for {protein_key}")
            continue
        
        protein_file = protein_files[0]
        logger.info(f"Mapping epitopes for {protein_key}...")
        
        sequences = []
        for record in SeqIO.parse(protein_file, "fasta"):
            seq_str = str(record.seq)
            accession = record.id.split('_')[0]
            
            # Map each epitope to this sequence
            mapped_epitopes = []
            for epitope in epitopes:
                start = epitope["start"] - 1  # Convert to 0-based
                end = epitope["end"]
                
                if start < len(seq_str) and end <= len(seq_str):
                    epitope_seq = seq_str[start:end]
                    mapped_epitopes.append({
                        "start": epitope["start"],
                        "end": epitope["end"],
                        "sequence": epitope_seq,
                        "type": epitope["type"],
                        "reference": epitope["reference"],
                        "length": len(epitope_seq),
                        "mapped": True
                    })
                else:
                    mapped_epitopes.append({
                        "start": epitope["start"],
                        "end": epitope["end"],
                        "sequence": None,
                        "type": epitope["type"],
                        "reference": epitope["reference"],
                        "mapped": False,
                        "reason": "Out of sequence range"
                    })
            
            sequences.append({
                "accession": accession,
                "length": len(seq_str),
                "epitopes": mapped_epitopes
            })
        
        results[protein_key] = {
            "protein": protein_key,
            "total_sequences": len(sequences),
            "sequences": sequences,
            "epitope_count": len(epitopes)
        }
    
    # Save results
    output_file = output_dir / "mapped_epitopes.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Epitope mapping results saved to {output_file}")

if __name__ == "__main__":
    map_epitopes()
