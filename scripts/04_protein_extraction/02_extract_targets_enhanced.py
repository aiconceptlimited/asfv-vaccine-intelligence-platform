#!/usr/bin/env python3
"""
Section 3.4: Target Protein Extraction (Enhanced)
Adds annotation status and extraction reason to output

Input:  data/raw/genomes/*.genbank
Output: data/interim/proteins/*.fasta
        data/metadata/protein_extraction_summary_enhanced.csv
        data/metadata/protein_extraction_report_enhanced.json

Author: Abubakar
Date: 2026-07-11
"""

import os
import sys
import json
import csv
import logging
import re
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
logger = setup_logger(__name__, "logs/extract/04_protein_extraction_enhanced.log")


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
# Enhanced Extraction Functions
# ============================================================
def is_target_protein(feature, target_synonyms):
    """Check if CDS feature matches target protein synonyms"""
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


def determine_annotation_status(feature, seq):
    """
    Determine annotation status and extraction reason
    
    Returns:
        tuple: (annotation_status, extraction_reason)
    """
    # Check for partial annotation
    is_partial = "partial" in str(feature.qualifiers).lower()
    
    # Check for internal stop codons (excluding terminal stop)
    has_internal_stop = "*" in seq[:-1] if seq else False
    
    # Check for missing start codon
    has_start = seq.startswith("M") if seq else False
    
    # Check for frameshift (look for frameshift in qualifiers)
    has_frameshift = "frameshift" in str(feature.qualifiers).lower()
    
    # Check for pseudogene
    is_pseudogene = "pseudogene" in str(feature.qualifiers).lower()
    
    # Determine annotation status
    if is_pseudogene:
        annotation_status = "pseudogene"
    elif is_partial:
        annotation_status = "partial"
    elif has_internal_stop:
        annotation_status = "internal_stop"
    elif has_frameshift:
        annotation_status = "frameshift"
    elif not has_start:
        annotation_status = "no_start_codon"
    else:
        annotation_status = "complete"
    
    # Determine extraction reason
    if annotation_status == "complete":
        reason = "full CDS"
    elif annotation_status == "partial":
        reason = "partial CDS annotation"
    elif annotation_status == "internal_stop":
        reason = "internal stop codon"
    elif annotation_status == "frameshift":
        reason = "frameshift detected"
    elif annotation_status == "no_start_codon":
        reason = "missing start codon"
    elif annotation_status == "pseudogene":
        reason = "annotated as pseudogene"
    else:
        reason = "unknown"
    
    return annotation_status, reason


def extract_protein_enhanced(gbk_file, target_gene, target_info):
    """
    Extract target protein with enhanced annotation details
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
        'annotation_status': 'absent',
        'extraction_reason': 'annotation missing',
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
                            
                            # Determine annotation status and reason
                            annotation_status, reason = determine_annotation_status(feature, seq)
                            result['annotation_status'] = annotation_status
                            result['extraction_reason'] = reason
                            
                            # Check completeness
                            has_start = seq.startswith("M")
                            has_stop = "*" in seq[:-1] if seq else False
                            
                            # Determine status based on length and annotation
                            if len(seq) >= expected * 0.90 and annotation_status == "complete":
                                status = "FULL_LENGTH"
                                result['notes'].append(f"Full-length ({len(seq)} aa)")
                            elif len(seq) >= expected * 0.75:
                                status = "TRUNCATED"
                                result['notes'].append(f"Truncated ({len(seq)} aa)")
                            elif len(seq) >= expected * 0.25:
                                status = "SEVERELY_TRUNCATED"
                                result['notes'].append(f"Severely truncated ({len(seq)} aa)")
                            else:
                                status = "FRAGMENT"
                                result['notes'].append(f"Fragment ({len(seq)} aa)")
                            
                            if annotation_status != "complete":
                                result['notes'].append(f"Annotation: {annotation_status}")
                            if reason != "full CDS":
                                result['notes'].append(f"Reason: {reason}")
                            
                            result['status'] = status
                            return result
                        else:
                            result['notes'].append("CDS found but no translation")
                            result['status'] = "NO_TRANSLATION"
                            result['annotation_status'] = "no_translation"
                            result['extraction_reason'] = "CDS without translation"
                            return result
        
        # If we get here, protein not found
        result['notes'].append("Not found in annotation")
        
    except Exception as e:
        logger.error(f"  {accession} {target_gene}: Error - {e}")
        result['status'] = "ERROR"
        result['annotation_status'] = "error"
        result['extraction_reason'] = str(e)
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
            result = extract_protein_enhanced(gbk_file, target_gene, target_info)
            gene_results.append(result)
            
            if result['sequence']:
                desc = f"{result['accession']}|{target_gene}|{result['length']}aa|{result['status']}"
                record = SeqRecord(Seq(result['sequence']), id=desc, description="")
                sequences.append(record)
            
            # Log status with details
            logger.info(f"  {result['accession']}: {result['status']} ({result['length']} aa) - {result['extraction_reason']}")
        
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
    
    # Generate enhanced summary CSV
    csv_path = metadata_dir / "protein_extraction_summary_enhanced.csv"
    
    fieldnames = [
        'accession', 'gene', 'protein', 'status', 'length',
        'annotation_status', 'extraction_reason', 'notes'
    ]
    
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
                    'annotation_status': r['annotation_status'],
                    'extraction_reason': r['extraction_reason'],
                    'notes': '; '.join(r['notes'])
                })
    
    logger.info(f"Enhanced summary CSV saved: {csv_path}")
    
    # Generate enhanced JSON report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_genomes': len(gbk_files),
        'target_proteins': TARGET_PROTEINS,
        'results': all_results,
        'summary': {}
    }
    
    # Calculate summary statistics
    for gene, results in all_results.items():
        status_counts = {}
        reason_counts = {}
        for r in results:
            status = r['status']
            reason = r['extraction_reason']
            status_counts[status] = status_counts.get(status, 0) + 1
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        report['summary'][gene] = {
            'status_counts': status_counts,
            'reason_counts': reason_counts,
            'total': len(results)
        }
    
    json_path = metadata_dir / "protein_extraction_report_enhanced.json"
    write_json(report, json_path)
    logger.info(f"Enhanced JSON report saved: {json_path}")
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SECTION 3.4: TARGET PROTEIN EXTRACTION (ENHANCED) COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total genomes: {len(gbk_files)}")
    logger.info(f"Target proteins: {len(TARGET_PROTEINS)}")
    logger.info("-" * 40)
    
    for gene, summary in report['summary'].items():
        protein = TARGET_PROTEINS[gene]['protein']
        status_str = ", ".join([f"{k}: {v}" for k, v in summary['status_counts'].items()])
        logger.info(f"  {protein} ({gene}): {status_str}")
    
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
