#!/usr/bin/env python3
"""
Section 3.3.1: Primary Data Source - Genome Acquisition
Downloads 11 ASFV genomes from NCBI GenBank

This script uses the src/asfv_platform/ package.
"""

import os
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asfv_platform.config import load_config
from asfv_platform.ncbi import download_genbank_record, download_fasta_record, extract_metadata, NCBIClientError
from asfv_platform.validation import validate_accession, verify_genome_file
from asfv_platform.io import ensure_directory, read_manifest, write_json
from asfv_platform.io.reports import create_download_report
from asfv_platform.utils import setup_logger

# Setup logger
logger = setup_logger(__name__, "logs/download/03_download.log")

def main():
    """Main execution"""
    # Load configuration
    config = load_config()
    
    # Get email from config or environment
    email = os.environ.get('NCBI_EMAIL')
    if not email:
        logger.error("NCBI_EMAIL environment variable not set")
        sys.exit(1)
    
    # Define paths
    manifest_path = PROJECT_ROOT / "workflow/resources/accession_manifest.txt"
    output_dir = PROJECT_ROOT / "data/raw/genomes"
    metadata_dir = PROJECT_ROOT / "data/metadata"
    
    ensure_directory(output_dir)
    ensure_directory(metadata_dir)
    
    # Read manifest
    genomes = read_manifest(manifest_path)
    if not genomes:
        logger.error("No genomes found in manifest")
        sys.exit(1)
    
    logger.info(f"Target genomes: {len(genomes)}")
    
    # Validate manifest
    valid_genomes = []
    invalid_genomes = []
    for g in genomes:
        if validate_accession(g.get('accession', '')):
            valid_genomes.append(g)
        else:
            invalid_genomes.append(g)
    
    if invalid_genomes:
        logger.warning(f"Found {len(invalid_genomes)} invalid entries")
    
    # Download genomes
    results = []
    for genome in valid_genomes:
        accession = genome['accession']
        logger.info(f"Downloading {accession}...")
        
        result = {'accession': accession, 'success': False}
        try:
            record = download_genbank_record(accession, email)
            gb_path = output_dir / f"{accession}.genbank"
            with open(gb_path, 'w') as f:
                from Bio import SeqIO
                SeqIO.write(record, f, "genbank")
            result['genbank_file'] = str(gb_path)
            
            fasta_record = download_fasta_record(accession, email)
            fasta_path = output_dir / f"{accession}.fasta"
            with open(fasta_path, 'w') as f:
                from Bio import SeqIO
                SeqIO.write(fasta_record, f, "fasta")
            result['fasta_file'] = str(fasta_path)
            
            metadata = extract_metadata(record)
            metadata.update(genome)
            result['metadata'] = metadata
            result['success'] = True
            logger.info(f"  ✓ Downloaded {accession}")
        except NCBIClientError as e:
            result['error'] = str(e)
            logger.error(f"  ✗ Failed: {e}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"  ✗ Unexpected error: {e}")
        
        results.append(result)
    
    # Verify downloads
    verification = {'all_valid': True}
    for genome in valid_genomes:
        accession = genome['accession']
        gb_check = verify_genome_file(output_dir / f"{accession}.genbank")
        fa_check = verify_genome_file(output_dir / f"{accession}.fasta")
        verification[accession] = {'genbank': gb_check, 'fasta': fa_check}
        if not (gb_check['is_valid'] and fa_check['is_valid']):
            verification['all_valid'] = False
    
    # Generate report
    report = create_download_report(genomes, results, verification, output_dir, email)
    write_json(report, metadata_dir / "download_report.json")
    
    # Save failed downloads
    failed = [r for r in results if not r['success']]
    if failed:
        write_json({'failed': failed}, metadata_dir / "failed_downloads.json")
    
    # Summary
    logger.info("=" * 60)
    logger.info("DOWNLOAD COMPLETE")
    logger.info(f"Successful: {sum(1 for r in results if r['success'])}/{len(valid_genomes)}")
    logger.info(f"All verified: {verification['all_valid']}")
    logger.info("=" * 60)
    
    return 0 if (sum(1 for r in results if r['success']) == len(valid_genomes) and verification['all_valid']) else 1

if __name__ == "__main__":
    sys.exit(main())
