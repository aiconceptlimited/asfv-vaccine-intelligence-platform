#!/usr/bin/env python3
"""
Section 3.3.1: ENA Confirmation
Confirms all accessions exist in the European Nucleotide Archive

Input:  workflow/resources/accession_manifest.txt
Output: data/metadata/ena_confirmation.json
        data/metadata/ena_confirmation_report.md

Author: Abubakar
Date: 2026-07-15
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# All 11 accessions
ACCESSIONS = [
    "PV740684", "PV740683", "PQ375363", "PQ375362",
    "ON409979", "ON409982", "ON409983", "ON409980",
    "ON409981", "MW856068", "MW856067"
]

def check_ena(accession):
    """Check if accession exists in ENA"""
    
    # ENA XML API endpoint
    url = f"https://www.ebi.ac.uk/ena/browser/api/xml/{accession}"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Parse XML to get basic info
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.text)
            
            # Extract basic information
            info = {
                'accession': accession,
                'found': True,
                'status_code': response.status_code,
                'source': 'ENA',
                'verified_date': datetime.now().isoformat()
            }
            
            # Try to extract additional info
            for elem in root.iter():
                if 'accession' in elem.tag.lower():
                    info['ena_accession'] = elem.text
                    break
            
            return info
        else:
            return {
                'accession': accession,
                'found': False,
                'status_code': response.status_code,
                'source': 'ENA',
                'verified_date': datetime.now().isoformat(),
                'error': f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            'accession': accession,
            'found': False,
            'source': 'ENA',
            'verified_date': datetime.now().isoformat(),
            'error': str(e)
        }

def main():
    """Main function"""
    
    logger.info("=" * 60)
    logger.info("Section 3.3.1: ENA Confirmation")
    logger.info("=" * 60)
    
    results = []
    
    for acc in ACCESSIONS:
        logger.info(f"Checking {acc} in ENA...")
        result = check_ena(acc)
        results.append(result)
        
        status = "✅" if result['found'] else "❌"
        logger.info(f"  {status} {acc}: {result.get('error', 'Found')}")
    
    # Save results
    output_dir = Path("data/metadata")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "ena_confirmation.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    found = sum(1 for r in results if r['found'])
    total = len(results)
    
    report = f"""# ENA Confirmation Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Section:** 3.3.1 Primary Data Source

## Summary

| Metric | Value |
|--------|-------|
| Total Accessions | {total} |
| Found in ENA | {found} |
| Not Found | {total - found} |

## Results

| Accession | Found | Source | Date |
|-----------|-------|--------|------|
"""
    
    for r in results:
        status = "✅ Yes" if r['found'] else "❌ No"
        report += f"| {r['accession']} | {status} | ENA | {r['verified_date']} |\n"
    
    with open(output_dir / "ena_confirmation_report.md", "w") as f:
        f.write(report)
    
    logger.info(f"\nResults saved to: {output_dir}/ena_confirmation.json")
    logger.info(f"Report saved to: {output_dir}/ena_confirmation_report.md")
    
    # Return success if all found
    return 0 if found == total else 1

if __name__ == "__main__":
    sys.exit(main())
