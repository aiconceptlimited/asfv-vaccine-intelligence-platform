#!/usr/bin/env python3
"""
Section 3.4.1: IEDB Search
Searches for experimentally characterized ASFV epitopes in pigs

Input:  config/proteins.yaml
Output: data/metadata/iedb_search_results.json
        data/metadata/iedb_epitopes.csv

Author: Abubakar
Date: 2026-07-15
"""

import os
import sys
import json
import logging
import requests
import csv
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Target proteins
PROTEINS = ['B646L', 'CP204L', 'E183L', 'EP402R', 'CP2475L', 'CP312R']

def search_iedb_protein(protein_name):
    """Search IEDB for a specific protein"""
    
    # IEDB API query
    # Using the IEDB REST API
    base_url = "https://api.iedb.org/v3/epitope"
    
    params = {
        'source_organism': 'African swine fever virus',
        'host': 'Sus scrofa',
        'protein': protein_name,
        'format': 'json'
    }
    
    try:
        # Check if we have cached results
        cache_file = Path(f"data/metadata/iedb_cache_{protein_name}.json")
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Make API request
        logger.info(f"Searching IEDB for {protein_name}...")
        response = requests.get(base_url, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            # Save cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            return data
        else:
            logger.warning(f"IEDB API returned {response.status_code} for {protein_name}")
            return None
            
    except Exception as e:
        logger.error(f"IEDB search failed for {protein_name}: {e}")
        return None

def parse_iedb_results(data, protein_name):
    """Parse IEDB results"""
    
    if not data:
        return {'found': False, 'error': 'No data'}
    
    # Extract epitope information
    epitopes = []
    
    # Handle different response formats
    if 'epitopes' in data:
        for epitope in data['epitopes']:
            epitopes.append({
                'protein': protein_name,
                'epitope_id': epitope.get('id', 'N/A'),
                'sequence': epitope.get('sequence', 'N/A'),
                'assay_type': epitope.get('assay_type', 'N/A'),
                'host': epitope.get('host', 'Sus scrofa'),
                'response': epitope.get('response', 'N/A')
            })
    
    return {
        'found': len(epitopes) > 0,
        'protein': protein_name,
        'epitope_count': len(epitopes),
        'epitopes': epitopes[:20]  # First 20 epitopes
    }

def main():
    """Main function"""
    
    logger.info("=" * 60)
    logger.info("Section 3.4.1: IEDB Search")
    logger.info("=" * 60)
    
    results = {}
    all_epitopes = []
    
    for protein in PROTEINS:
        logger.info(f"\nSearching for {protein}...")
        
        data = search_iedb_protein(protein)
        result = parse_iedb_results(data, protein)
        
        results[protein] = result
        if result['found']:
            logger.info(f"  ✅ Found {result['epitope_count']} epitopes")
            all_epitopes.extend(result['epitopes'])
        else:
            logger.info(f"  ⚠️ No epitopes found")
    
    # Save results
    output_dir = Path("data/metadata")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    with open(output_dir / "iedb_search_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Save CSV
    if all_epitopes:
        with open(output_dir / "iedb_epitopes.csv", "w") as f:
            writer = csv.DictWriter(f, fieldnames=['protein', 'epitope_id', 'sequence', 'assay_type', 'host', 'response'])
            writer.writeheader()
            writer.writerows(all_epitopes)
        logger.info(f"Epitopes saved to: {output_dir}/iedb_epitopes.csv")
    
    # Summary
    found = sum(1 for r in results.values() if r.get('found', False))
    total = len(PROTEINS)
    
    logger.info(f"\nSummary:")
    logger.info(f"  Proteins with experimental epitopes: {found}/{total}")
    logger.info(f"  Total epitopes found: {len(all_epitopes)}")

if __name__ == "__main__":
    main()
