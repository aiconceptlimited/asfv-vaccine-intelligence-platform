#!/usr/bin/env python3
"""
Section 3.5.5: Pig Proteome - Complete (FIXED v2)
Downloads Sus scrofa proteome from multiple reliable sources
"""

import os
import sys
import json
import logging
import requests
import subprocess
from pathlib import Path
from datetime import datetime
import gzip
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_from_uniprot_fasta():
    """Download from UniProt using the simple fasta endpoint"""
    
    output_dir = Path("data/raw/reference")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "sus_scrofa_proteome.fasta"
    metadata_file = output_dir / "sus_scrofa_proteome_metadata.json"
    
    # Use the UniProt KB API with proper query for Sus scrofa
    # Taxonomy ID: 9823 (Sus scrofa)
    # Use different query format that's known to work
    queries = [
        # Query 1: Reference proteome
        "https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28organism_id%3A9823%29+AND+%28reviewed%3Atrue%29+AND+%28proteome%3AUP000008227%29",
        # Query 2: All reviewed proteins
        "https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28organism_id%3A9823%29+AND+%28reviewed%3Atrue%29",
        # Query 3: Swiss-Prot only
        "https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28taxonomy_id%3A9823%29+AND+%28reviewed%3Atrue%29",
        # Query 4: Using proteome ID directly
        "https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28proteome%3AUP000008227%29"
    ]
    
    for i, url in enumerate(queries, 1):
        logger.info(f"Trying query {i}...")
        try:
            response = requests.get(url, timeout=120, headers={"Accept": "text/plain"})
            if response.status_code == 200:
                content = response.text
                if content and content.startswith('>'):
                    with open(output_file, 'w') as f:
                        f.write(content)
                    
                    # Count sequences
                    seq_count = sum(1 for line in content.split('\n') if line.startswith('>'))
                    logger.info(f"✅ Downloaded {seq_count} sequences from query {i}")
                    
                    # Save metadata
                    metadata = {
                        "organism": "Sus scrofa (pig)",
                        "taxonomy_id": 9823,
                        "download_date": datetime.now().isoformat(),
                        "source": "UniProtKB",
                        "url": url,
                        "file": str(output_file),
                        "sequence_count": seq_count,
                        "status": "SUCCESS",
                        "validation_status": "PASS" if seq_count > 0 else "FAIL"
                    }
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    return seq_count > 0
            else:
                logger.warning(f"Query {i} failed with status {response.status_code}")
        except Exception as e:
            logger.warning(f"Query {i} error: {e}")
    
    # If all UniProt queries fail, try FTP download
    logger.info("Trying FTP download from EBI...")
    try:
        ftp_url = "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota/UP000008227_9823.fasta.gz"
        response = requests.get(ftp_url, timeout=120, stream=True)
        
        if response.status_code == 200:
            gz_file = output_dir / "temp_proteome.fasta.gz"
            with open(gz_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Decompress
            with gzip.open(gz_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Clean up
            gz_file.unlink()
            
            # Count sequences
            with open(output_file, 'r') as f:
                seq_count = sum(1 for line in f if line.startswith('>'))
            
            logger.info(f"✅ Downloaded {seq_count} sequences from FTP")
            
            # Save metadata
            metadata = {
                "organism": "Sus scrofa (pig)",
                "taxonomy_id": 9823,
                "download_date": datetime.now().isoformat(),
                "source": "UniProt FTP",
                "url": ftp_url,
                "file": str(output_file),
                "sequence_count": seq_count,
                "status": "SUCCESS",
                "validation_status": "PASS" if seq_count > 0 else "FAIL"
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return seq_count > 0
    except Exception as e:
        logger.error(f"FTP download failed: {e}")
    
    logger.error("All download methods failed")
    return False

def create_blast_db():
    """Create BLAST database from proteome"""
    
    fasta_file = Path("data/raw/reference/sus_scrofa_proteome.fasta")
    
    if not fasta_file.exists():
        logger.error("Proteome file not found")
        return False
    
    # Check if file has sequences
    with open(fasta_file, 'r') as f:
        content = f.read().strip()
        if not content or not content.startswith('>'):
            logger.error("Proteome file appears empty or invalid")
            return False
    
    try:
        cmd = f"makeblastdb -in {fasta_file} -dbtype prot -out data/raw/reference/sus_scrofa_proteome -title 'Sus_scrofa_proteome' -parse_seqids"
        logger.info("Creating BLAST database...")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info("✅ BLAST database created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ BLAST database creation failed: {e}")
        return False

def main():
    logger.info("=" * 60)
    logger.info("SECTION 3.5.5: PIG PROTEOME - COMPLETE (FIXED v2)")
    logger.info("=" * 60)
    
    if download_from_uniprot_fasta():
        if create_blast_db():
            logger.info("✅ COMPLETE: Sus scrofa proteome downloaded and indexed")
        else:
            logger.warning("Proteome downloaded but BLAST indexing failed")
    else:
        logger.error("❌ FAILED: Could not download proteome")
        logger.info("Manual download: https://www.uniprot.org/proteomes/UP000008227")
        sys.exit(1)

if __name__ == "__main__":
    main()
