#!/usr/bin/env python3
"""
Multi-Antigen Weighting Scheme
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Antigen data from extracted sequences
ANTIGENS = {
    "p72": {"gene": "B646L", "conservation": 99.1, "sequences": 9, "role": "Primary"},
    "p30": {"gene": "CP204L", "conservation": 95.7, "sequences": 9, "role": "Primary"},
    "pp220": {"gene": "CP2475L", "conservation": 97.9, "sequences": 8, "role": "Secondary"},
    "pCP312R": {"gene": "CP312R", "conservation": 96.4, "sequences": 9, "role": "Secondary"},
    "p54": {"gene": "E183L", "conservation": 94.3, "sequences": 8, "role": "Tertiary"},
    "CD2v_159": {"gene": "EP402R", "conservation": 91.4, "sequences": 7, "role": "Auxiliary"}
}

def calculate_weights():
    """Calculate weighting scheme"""
    
    total_conservation = sum(a["conservation"] for a in ANTIGENS.values())
    
    results = []
    for name, data in ANTIGENS.items():
        weight = data["conservation"] / total_conservation * 100
        results.append({
            "antigen": name,
            "gene": data["gene"],
            "conservation": data["conservation"],
            "sequences": data["sequences"],
            "role": data["role"],
            "weight_percent": round(weight, 1),
            "weight_fraction": round(weight / 100, 3)
        })
    
    results.sort(key=lambda x: x["weight_percent"], reverse=True)
    
    output_file = Path("data/processed/vaccine_design/antigen_weights.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("=" * 60)
    logger.info("ANTIGEN WEIGHTING SCHEME")
    logger.info("=" * 60)
    for r in results:
        logger.info(f"  {r['antigen']} ({r['gene']}): {r['weight_percent']}% (Role: {r['role']})")
    
    logger.info(f"\n✅ Weights saved to: {output_file}")
    return results

if __name__ == "__main__":
    calculate_weights()
