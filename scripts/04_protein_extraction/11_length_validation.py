#!/usr/bin/env python3
"""
Section 3.4.4: Protein Length Validation
Validates extracted proteins against expected lengths
"""

import json
import logging
from pathlib import Path
from Bio import SeqIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected lengths from literature
EXPECTED_LENGTHS = {
    "B646L": {"name": "p72", "expected": 646, "min": 630, "max": 660},
    "CP204L": {"name": "p30", "expected": 194, "min": 190, "max": 200},
    "E183L": {"name": "p54", "expected": 183, "min": 180, "max": 190},
    "EP402R": {"name": "CD2v", "expected": 402, "min": 395, "max": 410},
    "CP2475L": {"name": "pp220", "expected": 2475, "min": 2450, "max": 2500},
    "CP312R": {"name": "pCP312R", "expected": 312, "min": 305, "max": 320}
}

def validate_lengths():
    """Validate protein lengths against expected values"""
    
    protein_dir = Path("data/interim/proteins")
    output_dir = Path("data/processed/proteins")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for protein_key, info in EXPECTED_LENGTHS.items():
        protein_file = protein_dir / f"{protein_key}_{info['name']}_sequences.fasta"
        
        if not protein_file.exists():
            logger.warning(f"⚠️  {protein_file} not found")
            continue
        
        logger.info(f"Validating {protein_key} ({info['name']})...")
        
        sequences = []
        for record in SeqIO.parse(protein_file, "fasta"):
            seq_len = len(record.seq)
            sequences.append({
                "id": record.id,
                "length": seq_len,
                "valid": info["min"] <= seq_len <= info["max"],
                "status": "PASS" if info["min"] <= seq_len <= info["max"] else "FAIL"
            })
        
        # Overall validation
        all_valid = all(s["valid"] for s in sequences)
        
        results[protein_key] = {
            "name": info["name"],
            "expected_length": info["expected"],
            "min_allowed": info["min"],
            "max_allowed": info["max"],
            "sequences_found": len(sequences),
            "all_valid": all_valid,
            "sequences": sequences,
            "status": "PASS" if all_valid else "FAIL"
        }
        
        status = "✅ PASS" if all_valid else "❌ FAIL"
        logger.info(f"  {status} - {len(sequences)} sequences, all within {info['min']}-{info['max']} aa")
    
    # Save results
    output_file = output_dir / "length_validation.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Length validation results saved to {output_file}")
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    logger.info(f"\n📊 Summary: {passed}/{total} proteins passed length validation")

if __name__ == "__main__":
    validate_lengths()
