#!/usr/bin/env python3
"""
HP-F.0 SEQUENCE VALIDATION PIPELINE
Validates that we have full-length, traceable sequences for Hp-F.0 alleles
"""

import os
import json
import hashlib
import re
from datetime import datetime

# Configuration
IPD_FASTA = "data/raw/ipd_mhc/MHC_prot.fasta"
GENBANK_DIR = "data/raw/genbank"
OUTPUT_FILE = "data/verified/kenyan_sla/hp_f0_validation.json"

# Define the Hp-F.0 alleles we need
HP_F0_ALLELES = [
    {
        'paper_designation': 'SLA-1*1501/1502',
        'locus': 'SLA-1',
        'genbank_accession': None,
        'ipd_mhc_search': ['SLA-1*15:01', 'SLA-1*15:02'],
        'notes': 'Group designation; needs resolution to official allele'
    },
    {
        'paper_designation': 'NS#16',
        'locus': 'SLA-2',
        'genbank_accession': 'KT351008',
        'ipd_mhc_search': ['SLA-2*08', 'SLA-2*06bm03'],
        'notes': 'Novel allele; partial sequence (282 nt)'
    },
    {
        'paper_designation': 'SLA-3*04hb06',
        'locus': 'SLA-3',
        'genbank_accession': None,
        'ipd_mhc_search': ['SLA-3*04:06'],
        'notes': 'Needs official name and sequence'
    }
]

def validate_sequence(sequence, seq_type='protein'):
    """Validate sequence quality"""
    if not sequence:
        return {'status': 'MISSING', 'length': 0}
    
    seq_len = len(sequence)
    
    if seq_type == 'protein':
        # Check if it looks like a protein sequence
        if not re.match(r'^[ACDEFGHIKLMNPQRSTVWY]+$', sequence):
            return {'status': 'INVALID', 'length': seq_len, 'reason': 'Contains non-protein characters'}
        
        # Full-length SLA class I is ~360-365 aa
        if seq_len >= 340:
            return {'status': 'FULL_LENGTH', 'length': seq_len, 'reason': 'Sequence length suggests full-length protein'}
        elif seq_len >= 200:
            return {'status': 'PARTIAL', 'length': seq_len, 'reason': f'Sequence is {seq_len} aa (expected ~360 aa)'}
        else:
            return {'status': 'PARTIAL', 'length': seq_len, 'reason': f'Sequence is only {seq_len} aa'}
    
    elif seq_type == 'nucleotide':
        # Full-length SLA coding sequence is ~1100 nt
        if seq_len >= 1000:
            return {'status': 'FULL_LENGTH', 'length': seq_len, 'reason': 'Sequence length suggests full-length coding sequence'}
        elif seq_len >= 200:
            return {'status': 'PARTIAL', 'length': seq_len, 'reason': f'Sequence is {seq_len} nt (expected ~1100 nt)'}
        else:
            return {'status': 'PARTIAL', 'length': seq_len, 'reason': f'Sequence is only {seq_len} nt'}

def read_fasta(filename):
    """Read FASTA file, return dictionary of header:sequence"""
    sequences = {}
    if not os.path.exists(filename):
        return sequences
    
    with open(filename, 'r') as f:
        content = f.read()
    
    records = content.split('>')[1:]
    for record in records:
        lines = record.split('\n')
        header = lines[0]
        seq = ''.join(lines[1:])
        sequences[header] = seq
    
    return sequences

def search_ipd_mhc(ipd_fasta, search_terms):
    """Search IPD-MHC FASTA for alleles"""
    results = []
    ipd_seqs = read_fasta(ipd_fasta)
    
    for header, seq in ipd_seqs.items():
        for term in search_terms:
            if term in header:
                results.append({
                    'header': header,
                    'sequence': seq,
                    'length': len(seq),
                    'search_term': term,
                    'accession': re.search(r'IPD-MHC:(\S+)', header).group(1) if re.search(r'IPD-MHC:(\S+)', header) else None
                })
                break
    
    return results

def main():
    print("="*80)
    print("HP-F.0 SEQUENCE VALIDATION PIPELINE")
    print("="*80)
    print(f"Started: {datetime.now().isoformat()}")
    
    validation_results = {}
    
    for allele in HP_F0_ALLELES:
        print(f"\n{'='*80}")
        print(f"Validating: {allele['paper_designation']}")
        print(f"  Locus: {allele['locus']}")
        print(f"  Notes: {allele['notes']}")
        print('='*80)
        
        result = {
            'paper_designation': allele['paper_designation'],
            'locus': allele['locus'],
            'genbank_accession': allele['genbank_accession'],
            'ipd_mhc_search': allele['ipd_mhc_search'],
            'sources': [],
            'best_sequence': None,
            'usable_for_netmhcpan': False,
            'validation_status': 'UNRESOLVED'
        }
        
        # 1. Search IPD-MHC
        print(f"\n  Searching IPD-MHC for: {', '.join(allele['ipd_mhc_search'])}")
        ipd_results = search_ipd_mhc(IPD_FASTA, allele['ipd_mhc_search'])
        
        if ipd_results:
            print(f"    ✅ Found {len(ipd_results)} records in IPD-MHC")
            for rec in ipd_results:
                print(f"      - {rec['header'][:60]}... ({rec['length']} aa)")
                
                # Validate sequence
                val = validate_sequence(rec['sequence'], 'protein')
                rec['validation'] = val
                rec['usable'] = val['status'] == 'FULL_LENGTH'
                
                source = {
                    'source': 'IPD-MHC',
                    'header': rec['header'],
                    'accession': rec['accession'],
                    'sequence': rec['sequence'][:100] + '...' if len(rec['sequence']) > 100 else rec['sequence'],
                    'length': rec['length'],
                    'status': val['status'],
                    'reason': val['reason'],
                    'usable': val['status'] == 'FULL_LENGTH'
                }
                result['sources'].append(source)
        else:
            print(f"    ❌ No records found in IPD-MHC")
        
        # 2. Check GenBank if accession exists
        if allele['genbank_accession']:
            genbank_file = f"{GENBANK_DIR}/{allele['genbank_accession']}.fasta"
            if os.path.exists(genbank_file):
                print(f"\n  Checking GenBank: {allele['genbank_accession']}")
                gb_seqs = read_fasta(genbank_file)
                if gb_seqs:
                    for header, seq in gb_seqs.items():
                        # Check if nucleotide or protein
                        if re.match(r'^[ACGTU]+$', seq.upper()):
                            seq_type = 'nucleotide'
                        else:
                            seq_type = 'protein'
                        
                        val = validate_sequence(seq, seq_type)
                        
                        source = {
                            'source': 'GenBank',
                            'header': header,
                            'accession': allele['genbank_accession'],
                            'sequence': seq[:100] + '...' if len(seq) > 100 else seq,
                            'length': len(seq),
                            'type': seq_type,
                            'status': val['status'],
                            'reason': val['reason'],
                            'usable': val['status'] == 'FULL_LENGTH'
                        }
                        result['sources'].append(source)
                        print(f"    ✅ Found: {header[:60]}... ({len(seq)} {seq_type}) - {val['status']}")
            else:
                print(f"\n  ❌ GenBank file not found: {genbank_file}")
        
        # 3. Determine best available sequence
        usable_sources = [s for s in result['sources'] if s.get('usable', False)]
        if usable_sources:
            # Use the longest usable sequence
            best = max(usable_sources, key=lambda x: x['length'])
            result['best_sequence'] = best
            result['usable_for_netmhcpan'] = True
            result['validation_status'] = 'RESOLVED'
            print(f"\n  ✅ USABLE SEQUENCE FOUND!")
            print(f"     Source: {best['source']}")
            print(f"     Length: {best['length']}")
            print(f"     Status: {best['status']}")
        else:
            # Use the longest partial sequence if available
            if result['sources']:
                best = max(result['sources'], key=lambda x: x['length'])
                result['best_sequence'] = best
                result['usable_for_netmhcpan'] = False
                result['validation_status'] = 'PARTIAL'
                print(f"\n  ⚠️ PARTIAL SEQUENCE ONLY")
                print(f"     Source: {best['source']}")
                print(f"     Length: {best['length']}")
                print(f"     Status: {best['status']}")
            else:
                result['validation_status'] = 'MISSING'
                print(f"\n  ❌ NO SEQUENCE FOUND")
        
        validation_results[allele['paper_designation']] = result
    
    # 4. Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for allele, result in validation_results.items():
        status = result['validation_status']
        if status == 'RESOLVED':
            symbol = '✅'
        elif status == 'PARTIAL':
            symbol = '⚠️'
        else:
            symbol = '❌'
        
        print(f"  {symbol} {allele}: {status} {'(usable for NetMHCpan)' if result['usable_for_netmhcpan'] else '(NOT usable)'}")
    
    # 5. Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(validation_results, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to: {OUTPUT_FILE}")
    
    # 6. Determine if we can proceed
    all_resolved = all(r['validation_status'] == 'RESOLVED' for r in validation_results.values())
    if all_resolved:
        print("\n✅ ALL HP-F.0 ALLELES ARE RESOLVED AND USABLE")
        print("   NetMHCpan can proceed!")
    else:
        print("\n❌ NOT ALL HP-F.0 ALLELES ARE RESOLVED")
        print("   Need to resolve the following:")
        for allele, result in validation_results.items():
            if result['validation_status'] != 'RESOLVED':
                print(f"     - {allele}: {result['validation_status']}")

if __name__ == "__main__":
    main()
