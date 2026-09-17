#!/usr/bin/env python3
"""
HP-F.0 VALIDATION GATE
Automated STOP conditions for sequence resolution
"""

import os
import json
import re
from datetime import datetime

# Configuration
VALIDATION_FILE = "data/verified/kenyan_sla/hp_f0_validation.json"
OUTPUT_FILE = "data/verified/kenyan_sla/hp_f0_status_gate.txt"

# Define required validation criteria
REQUIRED_CRITERIA = {
    "SLA-1*1501/1502": {
        "needs_accession": True,
        "needs_full_length": True,
        "min_length": 340,
        "notes": "Must resolve to official allele with full-length sequence"
    },
    "NS#16": {
        "needs_accession": True,
        "needs_full_length": True,
        "min_length": 340,
        "notes": "KT351008 is partial; need full-length SLA-2*08 sequence"
    },
    "SLA-3*04hb06": {
        "needs_accession": True,
        "needs_full_length": True,
        "min_length": 340,
        "notes": "Must resolve to official allele with full-length sequence"
    }
}

def check_validation_status(validation_file):
    """Check if all Hp-F.0 alleles pass validation"""
    
    if not os.path.exists(validation_file):
        return {
            'status': 'FAILED',
            'reason': 'Validation file not found',
            'alleles': {}
        }
    
    with open(validation_file, 'r') as f:
        data = json.load(f)
    
    results = {}
    all_passed = True
    
    for allele, criteria in REQUIRED_CRITERIA.items():
        if allele in data:
            allele_data = data[allele]
            status = allele_data.get('validation_status', 'UNRESOLVED')
            usable = allele_data.get('usable_for_netmhcpan', False)
            
            # Check if accession exists
            has_accession = allele_data.get('genbank_accession') is not None
            
            # Check if full-length
            is_full_length = False
            best = allele_data.get('best_sequence')
            if best:
                is_full_length = best.get('status') == 'FULL_LENGTH'
            
            # Determine pass/fail
            passed = (status == 'RESOLVED' and usable and is_full_length)
            
            results[allele] = {
                'status': status,
                'usable': usable,
                'has_accession': has_accession,
                'is_full_length': is_full_length,
                'passed': passed,
                'notes': criteria['notes']
            }
            
            if not passed:
                all_passed = False
        else:
            results[allele] = {
                'status': 'MISSING',
                'usable': False,
                'has_accession': False,
                'is_full_length': False,
                'passed': False,
                'notes': criteria['notes']
            }
            all_passed = False
    
    return {
        'status': 'PASSED' if all_passed else 'BLOCKED',
        'alleles': results,
        'timestamp': datetime.now().isoformat()
    }

def main():
    print("="*80)
    print("HP-F.0 VALIDATION GATE")
    print("="*80)
    
    result = check_validation_status(VALIDATION_FILE)
    
    print(f"\nTimestamp: {result['timestamp']}")
    print(f"\nOverall Status: {result['status']}")
    print("\n" + "="*80)
    print("ALLELE STATUS")
    print("="*80)
    
    for allele, info in result['alleles'].items():
        symbol = '✅' if info['passed'] else '❌'
        print(f"\n{symbol} {allele}")
        print(f"   Status: {info['status']}")
        print(f"   Usable: {info['usable']}")
        print(f"   Accession: {'Yes' if info['has_accession'] else 'No'}")
        print(f"   Full-length: {'Yes' if info['is_full_length'] else 'No'}")
        print(f"   Notes: {info['notes']}")
    
    print("\n" + "="*80)
    print("GATE STATUS")
    print("="*80)
    
    if result['status'] == 'PASSED':
        print("✅ ALL HP-F.0 ALLELES PASS VALIDATION")
        print("   NetMHCpan may proceed")
    else:
        print("❌ HP-F.0 VALIDATION GATE BLOCKED")
        print("   Cannot proceed to NetMHCpan")
        print("\n   Required actions:")
        for allele, info in result['alleles'].items():
            if not info['passed']:
                print(f"     - {allele}: {info['notes']}")
    
    # Save gate status
    with open(OUTPUT_FILE, 'w') as f:
        f.write(f"HP-F.0 VALIDATION GATE\n")
        f.write(f"{'='*80}\n")
        f.write(f"Timestamp: {result['timestamp']}\n")
        f.write(f"Status: {result['status']}\n")
        f.write(f"\nAllele Status:\n")
        for allele, info in result['alleles'].items():
            f.write(f"  {allele}: {info['status']} (passed: {info['passed']})\n")
    
    print(f"\n✅ Gate status saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
