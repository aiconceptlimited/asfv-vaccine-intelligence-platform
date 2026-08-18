#!/usr/bin/env python3
"""
CD2v Annotation Validation (Fixed)
Uses same search logic as extraction script

Author: Abubakar
Date: 2026-07-12
"""

import json
import csv
from pathlib import Path
from Bio import SeqIO

# Synonyms matching extraction script
CD2V_SYNONYMS = ["EP402R", "CD2v", "CD2", "CD2-like", "glycoprotein"]
SEARCH_QUALIFIERS = ["gene", "product", "note", "locus_tag", "protein_id"]

def is_cd2v(feature):
    """Check if CDS feature is CD2v using extraction script logic"""
    for qual in SEARCH_QUALIFIERS:
        value = feature.qualifiers.get(qual, [""])[0]
        if value:
            value_lower = value.lower()
            for syn in CD2V_SYNONYMS:
                if syn.lower() in value_lower:
                    return True
    return False

def validate_cd2v(gbk_file):
    """Validate CD2v annotation using extraction logic"""
    accession = gbk_file.stem
    result = {
        'accession': accession,
        'found': False,
        'gene': None,
        'product': None,
        'note': None,
        'locus_tag': None,
        'protein_id': None,
        'length': 0,
        'start_codon': None,
        'stop_codon': None,
        'has_valid_start': False,
        'has_valid_stop': False,
        'status': 'NOT_FOUND'
    }
    
    try:
        for record in SeqIO.parse(gbk_file, "genbank"):
            for feature in record.features:
                if feature.type == "CDS" and is_cd2v(feature):
                    result['found'] = True
                    result['gene'] = feature.qualifiers.get("gene", [""])[0]
                    result['product'] = feature.qualifiers.get("product", [""])[0]
                    result['note'] = feature.qualifiers.get("note", [""])[0]
                    result['locus_tag'] = feature.qualifiers.get("locus_tag", [""])[0]
                    result['protein_id'] = feature.qualifiers.get("protein_id", [""])[0]
                    
                    if "translation" in feature.qualifiers:
                        prot = feature.qualifiers["translation"][0]
                        result['length'] = len(prot)
                        
                        # Check start/stop
                        result['start_codon'] = prot[:3] if len(prot) >= 3 else ""
                        result['has_valid_start'] = prot.startswith("M")
                        result['stop_codon'] = prot[-3:] if len(prot) >= 3 else ""
                        result['has_valid_stop'] = "*" in prot[:-1] if len(prot) > 1 else False
                        
                        # Determine status
                        if result['length'] >= 350 and not result['has_valid_stop']:
                            result['status'] = 'FULL_LENGTH'
                        elif result['length'] >= 200:
                            result['status'] = 'TRUNCATED'
                        elif result['length'] >= 100:
                            result['status'] = 'SEVERELY_TRUNCATED'
                        else:
                            result['status'] = 'FRAGMENT'
                    
                    return result
    except Exception as e:
        result['status'] = f'ERROR: {e}'
    
    return result

def main():
    """Main execution"""
    genomes_dir = Path("data/raw/genomes")
    results = []
    
    for gbk in sorted(genomes_dir.glob("*.genbank")):
        result = validate_cd2v(gbk)
        results.append(result)
        print(f"{result['accession']}: {result['status']} ({result['length']} aa) - Gene: {result['gene']}")
    
    # Save results
    with open("data/metadata/cd2v_validation_fixed.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Save CSV
    fieldnames = ['accession', 'found', 'gene', 'product', 'length', 'status', 'has_valid_start', 'has_valid_stop']
    with open("data/metadata/cd2v_validation_fixed.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, '') for k in fieldnames})
    
    print(f"\nResults saved to data/metadata/cd2v_validation_fixed.json")

if __name__ == "__main__":
    main()
