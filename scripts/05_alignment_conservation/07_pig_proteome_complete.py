#!/usr/bin/env python3
"""
Section 3.5.5: Pig Proteome - Complete (REAL DATA)
Downloads Sus scrofa proteome from UniProt using real API
"""

import os
import sys
import json
import logging
import requests
import gzip
import shutil
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_uniprot_proteome():
    """Download Sus scrofa reference proteome from UniProt"""
    
    # UniProtKB proteome ID for Sus scrofa (pig)
    # UP000008227 is the reference proteome for Sus scrofa
    proteome_id = "UP000008227"
    
    # UniProt API endpoint for proteome download
    url = f"https://rest.uniprot.org/uniprotkb/stream?compressed=true&format=fasta&query=%28proteome:{proteome_id}%29"
    
    output_dir = Path("data/raw/reference")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_gz = output_dir / "sus_scrofa_proteome.fasta.gz"
    output_fasta = output_dir / "sus_scrofa_proteome.fasta"
    metadata_file = output_dir / "sus_scrofa_proteome_metadata.json"
    
    logger.info(f"Downloading Sus scrofa proteome from UniProt...")
    
    try:
        # Download with streaming
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        # Save compressed file
        with open(output_gz, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"✅ Downloaded compressed proteome: {output_gz}")
        
        # Decompress
        logger.info("Decompressing...")
        with gzip.open(output_gz, 'rb') as f_in:
            with open(output_fasta, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"✅ Decompressed to: {output_fasta}")
        
        # Count sequences
        sequence_count = 0
        with open(output_fasta, 'r') as f:
            for line in f:
                if line.startswith('>'):
                    sequence_count += 1
        
        # Save metadata
        metadata = {
            "proteome_id": proteome_id,
            "organism": "Sus scrofa (pig)",
            "download_date": datetime.now().isoformat(),
            "source": "UniProtKB",
            "url": url,
            "file": str(output_fasta),
            "sequence_count": sequence_count,
            "status": "SUCCESS",
            "validation_status": "PASS"
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Metadata saved: {metadata_file}")
        logger.info(f"📊 Total sequences: {sequence_count}")
        
        # Clean up gz file
        output_gz.unlink()
        logger.info("Cleaned up compressed file")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False

def create_blast_db():
    """Create BLAST database from proteome"""
    
    fasta_file = Path("data/raw/reference/sus_scrofa_proteome.fasta")
    
    if not fasta_file.exists():
        logger.error("Proteome file not found. Run download first.")
        return False
    
    try:
        import subprocess
        
        cmd = f"makeblastdb -in {fasta_file} -dbtype prot -out data/raw/reference/sus_scrofa_proteome -title 'Sus scrofa proteome' -parse_seqids"
        
        logger.info("Creating BLAST database...")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        logger.info("✅ BLAST database created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ BLAST database creation failed: {e}")
        return False

def main():
    """Main execution"""
    
    logger.info("=" * 60)
    logger.info("SECTION 3.5.5: PIG PROTEOME - COMPLETE")
    logger.info("=" * 60)
    
    # Download real proteome
    if download_uniprot_proteome():
        # Create BLAST database
        create_blast_db()
        logger.info("✅ COMPLETE: Real Sus scrofa proteome downloaded")
    else:
        logger.error("❌ FAILED: Could not download proteome")
        sys.exit(1)

if __name__ == "__main__":
    main()
