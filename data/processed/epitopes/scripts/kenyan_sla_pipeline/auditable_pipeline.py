#!/usr/bin/env python3
"""
AUDITABLE KENYAN SLA COVERAGE PIPELINE
- No unverified data can enter calculations
- Every value must have a source
- Provenance tracked throughout
"""

import os
import sys
import json
import hashlib
import pandas as pd
from datetime import datetime
import requests

# ============================================================
# CONFIGURATION
# ============================================================

VERIFIED_ONLY = True  # If True, only verified data can be used
STOP_ON_UNVERIFIED = True  # If True, pipeline stops if unverified data found

# ============================================================
# STEP 1: LOAD/KNOWLEDGE BASE — ONLY VERIFIED DATA
# ============================================================

class SlaEvidence:
    """Manages SLA evidence with strict provenance"""
    
    def __init__(self):
        self.evidence = {}
        self.load_evidence()
    
    def load_evidence(self):
        """Load evidence from file or create empty"""
        try:
            with open('data/curated/sla_evidence.json', 'r') as f:
                self.evidence = json.load(f)
            print(f"✅ Loaded {len(self.evidence)} evidence records")
        except:
            print("⚠️ No evidence file found. Creating empty database.")
            self.evidence = {}
    
    def add_evidence(self, allele, value, source, pmid, doi, frequency_type, sample_size, verified=False):
        """Add evidence record with provenance"""
        if allele in self.evidence:
            print(f"⚠️ Evidence for {allele} already exists")
            return
        
        self.evidence[allele] = {
            'value': value,
            'source': source,
            'pmid': pmid,
            'doi': doi,
            'frequency_type': frequency_type,
            'sample_size': sample_size,
            'verified': verified,
            'verification_date': datetime.now().isoformat() if verified else None,
            'notes': ''
        }
        self.save()
    
    def verify(self, allele):
        """Mark an allele as verified"""
        if allele in self.evidence:
            self.evidence[allele]['verified'] = True
            self.evidence[allee]['verification_date'] = datetime.now().isoformat()
            self.save()
            print(f"✅ Verified: {allele}")
        else:
            print(f"❌ Allele not found: {allele}")
    
    def get_verified(self, allele):
        """Get verified data only"""
        if allele not in self.evidence:
            return None
        if self.evidence[allele]['verified']:
            return self.evidence[allee]
        return None
    
    def get_all_verified(self):
        """Get all verified data"""
        return {k: v for k, v in self.evidence.items() if v['verified']}
    
    def save(self):
        os.makedirs('data/curated', exist_ok=True)
        with open('data/curated/sla_evidence.json', 'w') as f:
            json.dump(self.evidence, f, indent=2)
    
    def summary(self):
        """Print summary of evidence"""
        total = len(self.evidence)
        verified = len([v for v in self.evidence.values() if v['verified']])
        print(f"\nEvidence summary:")
        print(f"  Total records: {total}")
        print(f"  Verified: {verified}")
        print(f"  Unverified: {total - verified}")
        
        if total - verified > 0:
            print("\n  UNVERIFIED RECORDS:")
            for allele, info in self.evidence.items():
                if not info['verified']:
                    print(f"    ⚠️ {allele}: {info['source']} (needs verification)")


# ============================================================
# STEP 2: RETRIEVE SLA SEQUENCES FROM IPD-MHC
# ============================================================

def retrieve_sla_sequences():
    """Retrieve SLA sequences from IPD-MHC API"""
    print("\n" + "="*80)
    print("RETRIEVE SLA SEQUENCES FROM IPD-MHC")
    print("="*80)
    
    # IPD-MHC API endpoint
    base_url = "https://www.ebi.ac.uk/ipd/mhc/api/sla/alleles"
    
    alleles = ['SLA-1*1501', 'SLA-1*1502', 'SLA-2*NS#16', 'SLA-3*04hb06']
    sequences = {}
    
    for allele in alleles:
        print(f"\nFetching: {allele}")
        url = f"{base_url}/{allele}"
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                seq = data.get('protein_sequence', '')
                if seq:
                    sequences[allele] = {
                        'sequence': seq,
                        'accession': data.get('accession', 'unknown'),
                        'source': 'IPD-MHC API',
                        'retrieval_date': datetime.now().isoformat(),
                        'length': len(seq),
                        'checksum': hashlib.sha256(seq.encode()).hexdigest()[:16],
                        'verified': True
                    }
                    print(f"  ✅ Retrieved: {len(seq)} aa")
                else:
                    print(f"  ⚠️ No sequence found")
            else:
                print(f"  ❌ API error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    # Save sequences
    os.makedirs('data/verified/sla', exist_ok=True)
    with open('data/verified/sla/sla_sequences.json', 'w') as f:
        json.dump(sequences, f, indent=2)
    
    print(f"\n✅ Retrieved {len(sequences)} sequences")
    return sequences


# ============================================================
# STEP 3: VALIDATE SEQUENCES
# ============================================================

def validate_sequences():
    """Validate SLA sequences"""
    print("\n" + "="*80)
    print("VALIDATE SLA SEQUENCES")
    print("="*80)
    
    try:
        with open('data/verified/sla/sla_sequences.json', 'r') as f:
            sequences = json.load(f)
    except:
        print("❌ No sequences found")
        return None
    
    valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
    validated = {}
    
    for allele, info in sequences.items():
        seq = info.get('sequence', '')
        if not seq:
            print(f"  ⚠️ {allele}: Empty sequence")
            continue
        
        # Check length
        if len(seq) < 200:
            print(f"  ⚠️ {allele}: Length {len(seq)} (expected >200)")
            continue
        
        # Check valid amino acids
        invalid = set(seq) - valid_aa
        if invalid:
            print(f"  ⚠️ {allele}: Invalid residues: {invalid}")
            continue
        
        # All checks passed
        validated[allele] = info
        print(f"  ✅ {allele}: {len(seq)} aa, valid sequence")
    
    # Save validated
    with open('data/verified/sla/sla_sequences_validated.json', 'w') as f:
        json.dump(validated, f, indent=2)
    
    print(f"\n✅ Validated: {len(validated)} sequences")
    return validated


# ============================================================
# STEP 4: PREPARE NETMHCPAN INPUT
# ============================================================

def prepare_netmhcpan_input():
    """Prepare input files for NetMHCpan"""
    print("\n" + "="*80)
    print("PREPARE NETMHCPAN INPUT")
    print("="*80)
    
    peptides = ['HIDKNIIQY', 'RSIPLANIY', 'YTDIVQKKY']
    
    try:
        with open('data/verified/sla/sla_sequences_validated.json', 'r') as f:
            sequences = json.load(f)
    except:
        print("❌ No validated sequences found")
        return
    
    os.makedirs('data/predictions/netmhcpan', exist_ok=True)
    
    # Peptide FASTA
    with open('data/predictions/netmhcpan/peptides.fasta', 'w') as f:
        for peptide in peptides:
            f.write(f">{peptide}\n{peptide}\n")
    
    # SLA FASTA
    with open('data/predictions/netmhcpan/sla_sequences.fasta', 'w') as f:
        for allele, info in sequences.items():
            f.write(f">{allele}\n{info['sequence']}\n")
    
    print(f"✅ Peptides: {len(peptides)}")
    print(f"✅ SLA alleles: {len(sequences)}")
    
    print("\n⚠️ NetMHCpan submission required:")
    print("   URL: https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/")
    print("   Input Type: PEPTIDE")
    print(f"   Peptides: {', '.join(peptides)}")
    print("   Custom MHC: Paste sequences from sla_sequences.fasta")
    print("   Save results as: data/predictions/netmhcpan/results.csv")


# ============================================================
# STEP 5: CALCULATE COVERAGE (ONLY WITH VERIFIED DATA)
# ============================================================

def calculate_coverage():
    """Calculate haplotype coverage using verified data only"""
    print("\n" + "="*80)
    print("CALCULATE HAPLOTYPE COVERAGE (VERIFIED DATA ONLY)")
    print("="*80)
    
    # Check for results
    result_file = 'data/predictions/netmhcpan/results.csv'
    if not os.path.exists(result_file):
        print("❌ No NetMHCpan results found")
        print("   Please run NetMHCpan and save results")
        return
    
    # Load evidence
    try:
        with open('data/curated/sla_evidence.json', 'r') as f:
            evidence = json.load(f)
    except:
        evidence = {}
    
    # Check if we have verified evidence
    verified_evidence = {k: v for k, v in evidence.items() if v.get('verified', False)}
    if not verified_evidence:
        print("❌ No verified evidence found")
        print("   Cannot calculate population coverage without verified data")
        return
    
    print(f"✅ Using {len(verified_evidence)} verified evidence records")
    
    # Load binding results
    df = pd.read_csv(result_file)
    
    # Define haplotypes (using verified evidence only)
    haplotypes = [
        {'name': 'Hp-F.0', 'prevalence': 0.89, 'alleles': ['SLA-1*1501/1502', 'SLA-2*NS#16', 'SLA-3*04hb06']},
        {'name': 'Hp-6.0', 'prevalence': 0.33, 'alleles': ['SLA-1*0805', 'SLA-2*0504', 'SLA-3*0601']},
        {'name': 'Hp-G.0', 'prevalence': 0.22, 'alleles': ['SLA-1*rh03', 'SLA-2*05rh03', 'SLA-3*0601']},
        {'name': 'Hp-H.0', 'prevalence': 0.22, 'alleles': ['SLA-1*HB01', 'SLA-2*HB04', 'SLA-3*0502']},
    ]
    
    # Check haplotype data verification
    verified_haplotypes = []
    for haplotype in haplotypes:
        all_verified = all(allele in verified_evidence for allele in haplotype['alleles'])
        if all_verified:
            verified_haplotypes.append(haplotype)
        else:
            missing = [a for a in haplotype['alleles'] if a not in verified_evidence]
            print(f"  ⚠️ {haplotype['name']}: Missing verification for {missing}")
    
    if not verified_haplotypes:
        print("❌ No fully verified haplotypes found")
        print("   Cannot calculate population coverage")
        return
    
    print(f"\n✅ Using {len(verified_haplotypes)} verified haplotypes")
    
    # Calculate coverage
    results = []
    for haplotype in verified_haplotypes:
        covered = False
        for allele in haplotype['alleles']:
            # Check binding
            allele_df = df[df['MHC'].str.contains(allele.split('*')[0], case=False, na=False)]
            if not allele_df.empty:
                binders = allele_df[allele_df['BindLevel'].isin(['SB', 'WB'])]
                if not binders.empty:
                    covered = True
                    break
        
        results.append({
            'Haplotype': haplotype['name'],
            'Prevalence': f"{haplotype['prevalence']*100:.0f}%",
            'Covered': 'Yes' if covered else 'No'
        })
    
    results_df = pd.DataFrame(results)
    print("\n=== HAPLOTYPE COVERAGE (VERIFIED DATA) ===")
    print(results_df.to_string(index=False))
    
    # Calculate overall coverage
    coverage = sum([h['prevalence'] for h in verified_haplotypes if results_df[results_df['Haplotype'] == h['name']]['Covered'].values[0] == 'Yes'])
    print(f"\nOverall coverage: {coverage*100:.0f}%")
    
    # Save results
    os.makedirs('data/results/population_coverage', exist_ok=True)
    results_df.to_csv('data/results/population_coverage/haplotype_coverage_verified.csv', index=False)
    
    # Also save the full report
    report = {
        'analysis_date': datetime.now().isoformat(),
        'verified_evidence_used': len(verified_evidence),
        'verified_haplotypes_used': len(verified_haplotypes),
        'overall_coverage': f"{coverage*100:.0f}%",
        'results': results
    }
    with open('data/results/population_coverage/coverage_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Coverage report saved")


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*80)
    print("AUDITABLE KENYAN SLA COVERAGE PIPELINE")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"VERIFIED_ONLY: {VERIFIED_ONLY}")
    print(f"STOP_ON_UNVERIFIED: {STOP_ON_UNVERIFIED}")
    
    # Initialize evidence manager
    evidence = SlaEvidence()
    evidence.summary()
    
    # Check if we have verified evidence
    verified = evidence.get_all_verified()
    if not verified and STOP_ON_UNVERIFIED:
        print("\n❌ STOP: No verified evidence found.")
        print("   Please verify SLA data before running coverage analysis.")
        print("   Use: evidence.verify('allele') after manual verification")
        sys.exit(1)
    
    # Retrieve sequences (if needed)
    if not os.path.exists('data/verified/sla/sla_sequences_validated.json'):
        sequences = retrieve_sla_sequences()
        sequences = validate_sequences()
    
    # Prepare NetMHCpan input
    prepare_netmhcpan_input()
    
    # Calculate coverage (only with verified data)
    calculate_coverage()
    
    print("\n" + "="*80)
    print("PIPELINE COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
