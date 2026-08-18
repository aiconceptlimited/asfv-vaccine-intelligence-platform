#!/usr/bin/env python3
"""
Section 3.4: Target Protein Extraction
Extracts 6 target proteins from ASFV genomes

Targets:
- p72 (B646L) - Structural capsid protein
- p30 (CP204L) - Early expressed, immunogenic
- p54 (E183L) - Membrane protein, immunogenic
- CD2v (EP402R) - Protective antigen, serotype marker
- pp220 (CP2475L) - Polyprotein, structural
- pCP312R (CP312R) - Immunogenic potential

Input:  data/raw/genomes/*.genbank
Output: data/interim/proteins/*.fasta
        data/metadata/protein_extraction_summary.csv
        data/metadata/protein_extraction_report.json

Author: Abubakar
Date: 2026-07-11
"""

import os
import sys
import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asfv_platform.utils import setup_logger
from asfv_platform.io import ensure_directory, write_json

# Setup logger
logger = setup_logger(__name__, "logs/extract/04_protein_extraction.log")


# ============================================================
# Target Protein Definitions
# ============================================================
TARGET_PROTEINS = {
    'B646L': {
        'protein': 'p72',
        'expected_length': 646,
        'synonyms': ['B646L', 'p72', 'major capsid protein'],
        'evidence': 'Structural capsid protein'
    },
    'CP204L': {
        'protein': 'p30',
        'expected_length': 204,
        'synonyms': ['CP204L', 'p30'],
        'evidence': 'Early expressed, immunogenic'
    },
    'E183L': {
        'protein': 'p54',
        'expected_length': 183,
        'synonyms': ['E183L', 'p54'],
        'evidence': 'Membrane protein, immunogenic'
    },
    'EP402R': {
        'protein': 'CD2v',
        'expected_length': 402,
        'synonyms': ['EP402R', 'CD2v', 'CD2'],
        'evidence': 'Protective antigen, serotype marker'
    },
    'CP2475L': {
        'protein': 'pp220',
        'expected_length': 2475,
        'synonyms': ['CP2475L', 'pp220'],
        'evidence': 'Polyprotein, structural'
    },
    'CP312R': {
        'protein': 'pCP312R',
        'expected_length': 312,
        'synonyms': ['CP312R', 'pCP312R'],
        'evidence': 'Immunogenic potential'
    }
}


# ============================================================
# Functions
# ============================================================
def is_target_protein(feature, target_synonyms):
    """
    Check if a CDS feature matches target protein synonyms
    
    Args:
        feature: Biopython feature object
        target_synonyms: List of synonyms
    
    Returns:
        bool: True if match found
    """
    # Check gene qualifier
    gene = feature.qualifiers.get("gene", [""])[0] if "gene" in feature.qualifiers else ""
    if gene:
        gene_lower = gene.lower()
        for syn in target_synonyms:
            if syn.lower() == gene_lower:
                return True
    
    # Check product qualifier
    product = feature.qualifiers.get("product", [""])[0] if "product" in feature.qualifiers else ""
    if product:
        product_lower = product.lower()
        for syn in target_synonyms:
            if syn.lower() in product_lower:
                return True
    
    # Check locus_tag
    locus_tag = feature.qualifiers.get("locus_tag", [""])[0] if "locus_tag" in feature.qualifiers else ""
    if locus_tag:
        locus_lower = locus_tag.lower()
        for syn in target_synonyms:
            if syn.lower() in locus_lower:
                return True
    
    # Check note
    note = feature.qualifiers.get("note", [""])[0] if "note" in feature.qualifiers else ""
    if note:
        note_lower = note.lower()
        for syn in target_synonyms:
            if syn.lower() in note_lower:
                return True
    
    # Check protein_id
    protein_id = feature.qualifiers.get("protein_id", [""])[0] if "protein_id" in feature.qualifiers else ""
    if protein_id:
        pid_lower = protein_id.lower()
        for syn in target_synonyms:
            if syn.lower() in pid_lower:
                return True
    
    return False


def extract_protein(gbk_file, target_gene, target_info):
    """
    Extract target protein from GenBank file
    
    Args:
        gbk_file: Path to GenBank file
        target_gene: Gene name
        target_info: Target protein info dict
    
    Returns:
        dict: Extraction result
    """
    accession = gbk_file.stem
    synonyms = target_info['synonyms']
    expected = target_info['expected_length']
    
    result = {
        'accession': accession,
        'gene': target_gene,
        'protein': target_info['protein'],
        'found': False,
        'sequence': None,
        'length': 0,
        'status': 'NOT_FOUND',
        'notes': []
    }
    
    try:
        for record in SeqIO.parse(gbk_file, "genbank"):
            for feature in record.features:
                if feature.type == "CDS":
                    if is_target_protein(feature, synonyms):
                        result['found'] = True
                        
                        # Get translation
                        if "translation" in feature.qualifiers:
                            seq = feature.qualifiers["translation"][0]
                            result['sequence'] = seq
                            result['length'] = len(seq)
                            
                            # Check completeness
                            has_start = seq.startswith("M")
                            has_stop = "*" in seq[:-1] if seq else False
                            is_partial = "partial" in str(feature.qualifiers).lower()
                            
                            # Determine status
                            if len(seq) == expected:
                                status = "FULL_LENGTH"
                                result['notes'].append(f"Full-length ({len(seq)} aa)")
                            elif len(seq) >= expected * 0.9:
                                status = "FULL_LENGTH"
                                result['notes'].append(f"Near full-length ({len(seq)} aa)")
                            elif len(seq) > expected * 0.5:
                                status = "TRUNCATED"
                                result['notes'].append(f"Truncated ({len(seq)} aa)")
                                if is_partial:
                                    result['notes'].append("Marked as partial")
                            else:
                                status = "SHORT"
                                result['notes'].append(f"Short sequence ({len(seq)} aa)")
                            
                            if not has_start:
                                result['notes'].append("Missing start codon")
                            if has_stop:
                                result['notes'].append("Internal stop codon")
                            
                            result['status'] = status
                            
                            # Return first match found
                            return result
                        else:
                            result['notes'].append("CDS found but no translation")
                            result['status'] = "NO_TRANSLATION"
                            return result
        
        # If we get here, protein not found
        result['notes'].append("Not found in annotation")
        
    except Exception as e:
        logger.error(f"  {accession} {target_gene}: Error - {e}")
        result['status'] = "ERROR"
        result['notes'].append(str(e))
    
    return result


def main():
    """Main execution function"""
    
    # Define paths
    genomes_dir = PROJECT_ROOT / "data/raw/genomes"
    proteins_dir = PROJECT_ROOT / "data/interim/proteins"
    metadata_dir = PROJECT_ROOT / "data/metadata"
    
    ensure_directory(proteins_dir)
    ensure_directory(metadata_dir)
    
    # Find all GenBank files
    gbk_files = sorted(genomes_dir.glob("*.genbank"))
    
    if not gbk_files:
        logger.error(f"No GenBank files found in {genomes_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(gbk_files)} GenBank files")
    logger.info("=" * 60)
    
    # Initialize results storage
    all_results = {gene: [] for gene in TARGET_PROTEINS.keys()}
    
    # Extract each target protein
    for target_gene, target_info in TARGET_PROTEINS.items():
        logger.info(f"Extracting {target_info['protein']} ({target_gene})...")
        
        sequences = []
        gene_results = []
        
        for gbk_file in gbk_files:
            result = extract_protein(gbk_file, target_gene, target_info)
            gene_results.append(result)
            
            if result['sequence']:
                # Create SeqRecord for FASTA
                desc = f"{result['accession']}|{target_gene}|{result['length']}aa|{result['status']}"
                record = SeqRecord(Seq(result['sequence']), id=desc, description="")
                sequences.append(record)
            
            # Log status
            logger.info(f"  {result['accession']}: {result['status']} ({result['length']} aa)")
        
        all_results[target_gene] = gene_results
        
        # Save FASTA
        if sequences:
            fasta_path = proteins_dir / f"{target_gene}_{target_info['protein']}_sequences.fasta"
            with open(fasta_path, 'w') as f:
                SeqIO.write(sequences, f, "fasta")
            logger.info(f"  FASTA saved: {fasta_path} ({len(sequences)} sequences)")
        else:
            logger.warning(f"  No sequences found for {target_gene}")
        
        logger.info("-" * 40)
    
    # Generate summary CSV
    csv_path = metadata_dir / "protein_extraction_summary.csv"
    
    fieldnames = ['accession', 'gene', 'protein', 'status', 'length', 'notes']
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for gene, results in all_results.items():
            for r in results:
                writer.writerow({
                    'accession': r['accession'],
                    'gene': r['gene'],
                    'protein': r['protein'],
                    'status': r['status'],
                    'length': r['length'],
                    'notes': '; '.join(r['notes'])
                })
    
    logger.info(f"Summary CSV saved: {csv_path}")
    
    # Generate JSON report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_genomes': len(gbk_files),
        'target_proteins': TARGET_PROTEINS,
        'results': all_results,
        'summary': {}
    }
    
    # Calculate summary statistics
    for gene, results in all_results.items():
        full = sum(1 for r in results if r['status'] == 'FULL_LENGTH')
        trunc = sum(1 for r in results if r['status'] == 'TRUNCATED')
        not_found = sum(1 for r in results if r['status'] == 'NOT_FOUND')
        
        report['summary'][gene] = {
            'full_length': full,
            'truncated': trunc,
            'not_found': not_found,
            'total': len(results)
        }
    
    json_path = metadata_dir / "protein_extraction_report.json"
    write_json(report, json_path)
    logger.info(f"JSON report saved: {json_path}")
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SECTION 3.4: TARGET PROTEIN EXTRACTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total genomes: {len(gbk_files)}")
    logger.info(f"Target proteins: {len(TARGET_PROTEINS)}")
    logger.info("-" * 40)
    
    for gene, summary in report['summary'].items():
        protein = TARGET_PROTEINS[gene]['protein']
        logger.info(f"  {protein} ({gene}): {summary['full_length']} full, {summary['truncated']} truncated, {summary['not_found']} not found")
    
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
