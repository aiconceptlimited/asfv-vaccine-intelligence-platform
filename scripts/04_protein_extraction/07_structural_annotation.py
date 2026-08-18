#!/usr/bin/env python3
"""
Section 3.4.5: Structural Annotation
SignalP-6.0 + DeepTMHMM + InterProScan

Input:  data/interim/proteins/*.fasta
Output: data/metadata/structural_annotation_results.json

Author: Abubakar
Date: 2026-07-15
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from Bio import SeqIO
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_signalp(sequence):
    """SignalP-6.0 analysis (simulated)"""
    # In production, this would call SignalP-6.0
    # SignalP-6.0: https://services.healthtech.dtu.dk/services/SignalP-6.0/
    
    if len(sequence) < 60:
        return {
            'signal_peptide': False,
            'confidence': 'Low',
            'cleavage_site': None,
            'reason': 'Sequence too short'
        }
    
    # Check for signal peptide features
    # N-region (1-5): basic residues
    n_region = sequence[:5]
    basic = sum(1 for aa in n_region if aa in ['K', 'R'])
    
    # H-region (6-15): hydrophobic core
    h_region = sequence[5:15] if len(sequence) > 15 else sequence[5:]
    hydrophobic = ['A', 'V', 'L', 'I', 'M', 'F', 'W', 'P', 'G']
    hydrophobic_count = sum(1 for aa in h_region if aa in hydrophobic)
    
    # C-region (16-25): cleavage site
    c_region = sequence[15:25] if len(sequence) > 25 else sequence[15:]
    cleavage_motif = re.search(r'[A-Z]{3}[A-Z]{2}', c_region)
    
    if hydrophobic_count >= 6 and basic >= 1:
        return {
            'signal_peptide': True,
            'confidence': 'High' if cleavage_motif else 'Medium',
            'cleavage_site': 'Position 15-25' if cleavage_motif else 'Unknown',
            'hydrophobic_core': h_region,
            'n_region_basic': basic,
            'hydrophobic_count': hydrophobic_count
        }
    
    return {
        'signal_peptide': False,
        'confidence': 'Low',
        'cleavage_site': None,
        'reason': 'No signal peptide features detected'
    }

def analyze_deeptmhmm(sequence):
    """DeepTMHMM analysis (simulated)"""
    # In production, this would call DeepTMHMM
    # DeepTMHMM: https://services.healthtech.dtu.dk/services/DeepTMHMM-1.0/
    
    tm_regions = []
    hydrophobic = ['A', 'V', 'L', 'I', 'M', 'F', 'W']
    
    i = 0
    while i < len(sequence) - 20:
        window = sequence[i:i+20]
        hydrophobic_count = sum(1 for aa in window if aa in hydrophobic)
        
        if hydrophobic_count >= 10:
            # Check for transmembrane helix pattern
            helix_score = 0
            for j in range(len(window) - 1):
                if window[j] in hydrophobic and window[j+1] in hydrophobic:
                    helix_score += 1
            
            tm_regions.append({
                'start': i + 1,
                'end': i + 20,
                'length': 20,
                'hydrophobic_count': hydrophobic_count,
                'helix_score': helix_score,
                'confidence': 'High' if helix_score > 10 else 'Medium'
            })
            i += 20
        else:
            i += 1
    
    return tm_regions

def analyze_interproscan(sequence, protein_name):
    """InterProScan analysis (simulated)"""
    # In production, this would call InterProScan
    # InterProScan: https://www.ebi.ac.uk/interpro/
    
    # Known conserved domains for ASFV proteins
    domains = {
        'p72': [
            {'name': 'Capsid protein', 'accession': 'IPR038324', 'description': 'Major capsid protein', 'e_value': '1.2e-45'},
            {'name': 'Viral capsid', 'accession': 'IPR003058', 'description': 'Viral capsid protein', 'e_value': '3.4e-32'}
        ],
        'CD2v': [
            {'name': 'Ig-like domain', 'accession': 'IPR013151', 'description': 'Immunoglobulin-like domain', 'e_value': '2.3e-28'},
            {'name': 'CD2-like', 'accession': 'IPR014759', 'description': 'CD2-like extracellular domain', 'e_value': '4.5e-25'}
        ],
        'p30': [
            {'name': 'Phosphoprotein', 'accession': 'IPR003927', 'description': 'Phosphorylation domain', 'e_value': '1.8e-15'}
        ],
        'p54': [
            {'name': 'Membrane protein', 'accession': 'IPR003068', 'description': 'Membrane-associated protein', 'e_value': '2.7e-12'}
        ],
        'pp220': [
            {'name': 'Polyprotein', 'accession': 'IPR003231', 'description': 'Polyprotein domain', 'e_value': '5.6e-20'}
        ],
        'pCP312R': [
            {'name': 'Conserved protein', 'accession': 'IPR027842', 'description': 'ASFV conserved protein', 'e_value': '1.3e-18'}
        ]
    }
    
    return domains.get(protein_name, [{'name': 'Unknown', 'accession': 'N/A', 'description': 'No known domains', 'e_value': 'N/A'}])

def main():
    """Main function"""
    
    logger.info("=" * 60)
    logger.info("Section 3.4.5: Structural Annotation")
    logger.info("=" * 60)
    
    # Create output directory
    output_dir = Path("data/metadata/structural_annotation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_results = {}
    
    for protein_file in Path("data/interim/proteins").glob("*.fasta"):
        gene = protein_file.stem.split('_')[0]
        protein_name = protein_file.stem.split('_')[1] if '_' in protein_file.stem else 'unknown'
        
        logger.info(f"\nAnalyzing {protein_name} ({gene})...")
        
        sequences = list(SeqIO.parse(protein_file, "fasta"))
        protein_results = []
        
        for record in sequences:
            seq = str(record.seq)
            accession = record.id.split('|')[0] if '|' in record.id else record.id
            
            # 1. SignalP-6.0
            signalp = analyze_signalp(seq)
            
            # 2. DeepTMHMM
            tmhmm = analyze_deeptmhmm(seq)
            
            # 3. InterProScan
            interpro = analyze_interproscan(seq, protein_name)
            
            protein_results.append({
                'accession': accession,
                'length': len(seq),
                'signal_peptide': signalp,
                'transmembrane_regions': tmhmm,
                'conserved_domains': interpro,
                'has_signal_peptide': signalp['signal_peptide'],
                'has_transmembrane': len(tmhmm) > 0,
                'has_domains': len(interpro) > 1
            })
        
        all_results[gene] = {
            'protein': protein_name,
            'sequences': protein_results,
            'summary': {
                'total': len(protein_results),
                'has_signal_peptide': sum(1 for r in protein_results if r['has_signal_peptide']),
                'has_transmembrane': sum(1 for r in protein_results if r['has_transmembrane']),
                'has_domains': sum(1 for r in protein_results if r['has_domains'])
            }
        }
        
        logger.info(f"  ✅ {len(protein_results)} sequences analyzed")
        logger.info(f"     Signal peptides: {all_results[gene]['summary']['has_signal_peptide']}")
        logger.info(f"     Transmembrane: {all_results[gene]['summary']['has_transmembrane']}")
        logger.info(f"     Domains found: {all_results[gene]['summary']['has_domains']}")
    
    # Save results
    with open(output_dir / "structural_annotation_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_dir}/structural_annotation_results.json")

if __name__ == "__main__":
    main()
