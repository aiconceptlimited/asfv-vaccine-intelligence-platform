#!/usr/bin/env python3
"""
Section 3.3.2: Isolate Metadata Extraction
Parses GenBank annotations and builds structured metadata table

Input:  data/raw/genomes/*.genbank
Output: data/metadata/genome_metadata.csv
        data/metadata/genome_metadata.json

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

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asfv_platform.utils import setup_logger
from asfv_platform.io import ensure_directory, write_json

# Setup logger
logger = setup_logger(__name__, "logs/extract/02_metadata.log")


# ============================================================
# Functions
# ============================================================
def extract_metadata_from_genbank(gbk_file):
    """
    Extract metadata from a GenBank file
    
    Args:
        gbk_file: Path to GenBank file
    
    Returns:
        dict: Metadata dictionary
    """
    accession = gbk_file.stem
    metadata = {
        'accession': accession,
        'accession_version': None,
        'strain': None,
        'isolate': None,
        'country': None,
        'collection_date': None,
        'year': None,
        'host': None,
        'sample_source': None,
        'genotype': None,
        'genome_length': None,
        'gc_content': None,
        'ambiguous_nucleotides': None,
        'ambiguous_percent': None,
        'cds_count': None,
        'assembly_status': None,
        'sequencing_technology': None,
        'submitter': None,
        'publication': None,
        'organism': None,
        'taxonomy': None
    }
    
    try:
        for record in SeqIO.parse(gbk_file, "genbank"):
            # Accession
            metadata['accession_version'] = record.id
            
            # Genome length
            seq = str(record.seq)
            metadata['genome_length'] = len(seq)
            
            # GC content
            gc = (seq.count('G') + seq.count('C')) / len(seq) * 100
            metadata['gc_content'] = round(gc, 2)
            
            # Ambiguous nucleotides
            n_count = seq.count('N')
            metadata['ambiguous_nucleotides'] = n_count
            metadata['ambiguous_percent'] = round(n_count / len(seq) * 100, 2) if len(seq) > 0 else 0
            
            # CDS count
            cds_count = len([f for f in record.features if f.type == "CDS"])
            metadata['cds_count'] = cds_count
            
            # Assembly status
            if "complete" in str(record.annotations).lower():
                metadata['assembly_status'] = "Complete"
            else:
                metadata['assembly_status'] = "Unknown"
            
            # Organism
            if 'organism' in record.annotations:
                metadata['organism'] = record.annotations['organism']
            
            # Taxonomy
            if 'taxonomy' in record.annotations:
                metadata['taxonomy'] = '|'.join(record.annotations['taxonomy'])
            
            # Extract from features
            for feature in record.features:
                if feature.type == "source":
                    qualifiers = feature.qualifiers
                    
                    # Strain
                    if 'strain' in qualifiers:
                        metadata['strain'] = qualifiers['strain'][0]
                    elif 'isolate' in qualifiers:
                        metadata['strain'] = qualifiers['isolate'][0]
                    
                    # Isolate
                    if 'isolate' in qualifiers:
                        metadata['isolate'] = qualifiers['isolate'][0]
                    
                    # Country
                    if 'country' in qualifiers:
                        country = qualifiers['country'][0]
                        # Clean up country string (remove ":", ":", etc.)
                        metadata['country'] = country.split(':')[0].strip() if ':' in country else country
                    
                    # Collection date
                    if 'collection_date' in qualifiers:
                        metadata['collection_date'] = qualifiers['collection_date'][0]
                        # Extract year
                        try:
                            date_str = qualifiers['collection_date'][0]
                            if '-' in date_str:
                                metadata['year'] = int(date_str.split('-')[0])
                            elif len(date_str) == 4:
                                metadata['year'] = int(date_str)
                        except:
                            pass
                    
                    # Host
                    if 'host' in qualifiers:
                        metadata['host'] = qualifiers['host'][0]
                    
                    # Sample source
                    if 'sample_source' in qualifiers:
                        metadata['sample_source'] = qualifiers['sample_source'][0]
                    
                    # Genotype (from config, not GenBank)
                    # We'll merge this from the manifest later
            
            # Publication info
            if 'references' in record.annotations:
                refs = record.annotations['references']
                if refs:
                    # Get the first reference
                    first_ref = refs[0]
                    if hasattr(first_ref, 'title'):
                        metadata['publication'] = first_ref.title
            
            # Submitter
            if 'references' in record.annotations:
                refs = record.annotations['references']
                if refs:
                    first_ref = refs[0]
                    if hasattr(first_ref, 'authors'):
                        metadata['submitter'] = first_ref.authors
            
            # Sequencing technology
            # Look for "sequencing" or "platform" in comments
            if 'comment' in record.annotations:
                comment = record.annotations['comment']
                if 'sequencing' in comment.lower() or 'platform' in comment.lower():
                    # Extract platform info (simplified)
                    lines = comment.split('\n')
                    for line in lines:
                        if 'platform' in line.lower() or 'sequencing' in line.lower():
                            metadata['sequencing_technology'] = line.strip()
                            break
            
            break  # Only process first record
    
    except Exception as e:
        logger.error(f"Error processing {gbk_file}: {e}")
        metadata['error'] = str(e)
    
    return metadata


def merge_manifest_data(metadata_list, manifest_path):
    """
    Merge genotype and strain info from manifest
    
    Args:
        metadata_list: List of metadata dictionaries
        manifest_path: Path to accession manifest
    
    Returns:
        list: Updated metadata list
    """
    # Read manifest
    manifest_data = {}
    with open(manifest_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) >= 5:
                accession = parts[0].strip()
                manifest_data[accession] = {
                    'strain': parts[1].strip(),
                    'country': parts[2].strip(),
                    'genotype': parts[3].strip(),
                    'year': int(parts[4].strip())
                }
    
    # Merge manifest data
    for metadata in metadata_list:
        accession = metadata['accession']
        if accession in manifest_data:
            manifest_entry = manifest_data[accession]
            # Only fill if not already set
            if metadata['strain'] is None:
                metadata['strain'] = manifest_entry['strain']
            if metadata['country'] is None:
                metadata['country'] = manifest_entry['country']
            # Genotype from manifest (override)
            metadata['genotype'] = manifest_entry['genotype']
            if metadata['year'] is None:
                metadata['year'] = manifest_entry['year']
    
    return metadata_list


def main():
    """Main execution function"""
    
    # Define paths
    genomes_dir = PROJECT_ROOT / "data/raw/genomes"
    metadata_dir = PROJECT_ROOT / "data/metadata"
    manifest_path = PROJECT_ROOT / "workflow/resources/accession_manifest.txt"
    
    ensure_directory(metadata_dir)
    
    # Find all GenBank files
    gbk_files = sorted(genomes_dir.glob("*.genbank"))
    
    if not gbk_files:
        logger.error(f"No GenBank files found in {genomes_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(gbk_files)} GenBank files")
    
    # Extract metadata from each file
    all_metadata = []
    for gbk_file in gbk_files:
        logger.info(f"Processing: {gbk_file.stem}")
        metadata = extract_metadata_from_genbank(gbk_file)
        all_metadata.append(metadata)
        
        # Log key fields
        logger.info(f"  ✓ {metadata['accession']}: {metadata['genome_length']} bp, {metadata['cds_count']} CDS")
    
    # Merge manifest data
    all_metadata = merge_manifest_data(all_metadata, manifest_path)
    
    # Save as CSV
    csv_path = metadata_dir / "genome_metadata.csv"
    
    # Define field order
    fieldnames = [
        'accession', 'accession_version', 'strain', 'isolate', 'country',
        'location', 'collection_date', 'year', 'host', 'sample_source',
        'genotype', 'genome_length', 'gc_content', 'ambiguous_nucleotides',
        'ambiguous_percent', 'cds_count', 'assembly_status',
        'sequencing_technology', 'submitter', 'publication',
        'organism', 'taxonomy', 'download_date'
    ]
    
    # Add download_date
    download_date = datetime.now().isoformat()
    for metadata in all_metadata:
        metadata['download_date'] = download_date
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_metadata)
    
    logger.info(f"CSV metadata saved to: {csv_path}")
    
    # Save as JSON
    json_path = metadata_dir / "genome_metadata.json"
    write_json(all_metadata, json_path)
    logger.info(f"JSON metadata saved to: {json_path}")
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SECTION 3.3.2: METADATA EXTRACTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total genomes processed: {len(all_metadata)}")
    logger.info(f"CSV output: {csv_path}")
    logger.info(f"JSON output: {json_path}")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
