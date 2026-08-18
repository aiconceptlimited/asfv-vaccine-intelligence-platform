#!/usr/bin/env python3
"""
Section 3.4.1: IEDB Search (Manual)
Generates search URLs for manual query
"""

import json
from pathlib import Path

PROTEINS = ['B646L', 'CP204L', 'E183L', 'EP402R', 'CP2475L', 'CP312R']

def generate_search_url(protein):
    """Generate IEDB search URL"""
    
    base = "https://www.iedb.org/search/"
    params = {
        'source_organism': 'African swine fever virus',
        'host': 'Sus scrofa',
        'protein': protein
    }
    
    url = f"{base}?source_organism={params['source_organism']}&host={params['host']}&protein={params['protein']}"
    return url

def main():
    results = {}
    
    for protein in PROTEINS:
        url = generate_search_url(protein)
        results[protein] = {
            'search_url': url,
            'protein': protein,
            'host': 'Sus scrofa',
            'source_organism': 'African swine fever virus'
        }
        print(f"{protein}: {url}")
    
    with open("data/metadata/iedb_search_manual.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: data/metadata/iedb_search_manual.json")
    print("Please manually search these URLs in a web browser.")

if __name__ == "__main__":
    main()
