#!/usr/bin/env python3
"""
Download ASFV genomes from GenBank
"""

import os
import sys
import logging
import requests
from pathlib import Path
from Bio import Entrez, SeqIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ASFV genome accessions
ACCESSIONS = [
    "PV740684", "PV740683", "PQ375363", "PQ375362",
    "ON409979", "ON409982", "ON409983", "ON409980",
    "ON409981", "MW856068", "MW856067"
]

def download_genome(accession):
    """Download a single genome from GenBank"""
    
    output_dir = Path("data/raw/genomes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{accession}.gbff"
    
    if output_file.exists():
        logger.info(f"✅ {accession} already downloaded")
        return True
    
    logger.info(f"Downloading {accession}...")
    
    try:
        # Use Entrez
        Entrez.email = "your_email@example.com"  # Replace with your email
        handle = Entrez.efetch(db="nucleotide", id=accession, rettype="gb", retmode="text")
        content = handle.read()
        handle.close()
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"✅ Downloaded {accession}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {accession}: {e}")
        return False

def main():
    """Download all genomes"""
    
    logger.info("Downloading ASFV genomes...")
    
    successful = 0
    for acc in ACCESSIONS:
        if download_genome(acc):
            successful += 1
    
    logger.info(f"✅ Downloaded {successful}/{len(ACCESSIONS)} genomes")
    
    if successful == 0:
        logger.warning("No genomes downloaded. Please check internet connection and Entrez configuration.")

if __name__ == "__main__":
    main()
