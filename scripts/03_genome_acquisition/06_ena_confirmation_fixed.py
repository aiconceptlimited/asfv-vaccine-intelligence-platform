#!/usr/bin/env python3
"""
Section 3.3.1: ENA Confirmation (FIXED)
Uses ENA Browser API correctly
"""

import requests
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ACCESSIONS = [
    "PV740684", "PV740683", "PQ375363", "PQ375362",
    "ON409979", "ON409982", "ON409983", "ON409980",
    "ON409981", "MW856068", "MW856067"
]

def check_ena(accession):
    """Check accession in ENA using correct API"""
    
    # Use ENA Portal API (JSON format)
    url = f"https://www.ebi.ac.uk/ena/portal/api/search?result=assembly&query={accession}&format=json"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "accession": accession,
                    "found": True,
                    "status": "OK",
                    "data": data[0] if data else None
                }
            else:
                return {"accession": accession, "found": False, "status": "NOT_FOUND"}
        else:
            return {"accession": accession, "found": False, "status": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"accession": accession, "found": False, "status": f"ERROR: {str(e)}"}

def main():
    """Check all accessions"""
    
    logger.info("Checking ENA accessions...")
    results = []
    
    for acc in ACCESSIONS:
        logger.info(f"Checking {acc}...")
        result = check_ena(acc)
        results.append(result)
        
        if result['found']:
            logger.info(f"  ✅ {acc}: Found")
        else:
            logger.warning(f"  ❌ {acc}: {result['status']}")
    
    # Save results
    output_dir = Path("data/metadata")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "ena_confirmation.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Results saved to data/metadata/ena_confirmation.json")

if __name__ == "__main__":
    main()
