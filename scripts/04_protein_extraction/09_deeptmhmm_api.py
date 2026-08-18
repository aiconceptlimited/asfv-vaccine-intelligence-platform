#!/usr/bin/env python3
"""
Section 3.4.5: DeepTMHMM via API
Uses DTU BioLib's DeepTMHMM service
"""

import os
import sys
import json
import time
import logging
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def submit_deeptmhmm(protein_file):
    """
    Submit protein to DeepTMHMM web service
    """
    
    # Read protein sequences
    with open(protein_file, 'r') as f:
        sequences = f.read()
    
    # DTU BioLib API endpoint
    url = "https://dtu.biolib.com/DeepTMHMM/3/api/predict"
    
    try:
        logger.info(f"Submitting {Path(protein_file).name} to DeepTMHMM...")
        
        # Prepare multipart form data
        files = {
            'fasta': (Path(protein_file).name, sequences, 'text/plain')
        }
        data = {
            'format': 'json'
        }
        
        # Submit job
        response = requests.post(url, files=files, data=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        # Save results
        output_dir = Path("data/processed/deeptmhmm")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{Path(protein_file).stem}_deeptmhmm.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Parse results
        if 'results' in result:
            tmh = result['results'].get('TMH', [])
            logger.info(f"✅ Found {len(tmh)} transmembrane helices")
            logger.info(f"   Results saved to {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DeepTMHMM API failed: {e}")
        logger.info("   Please use web interface: https://dtu.biolib.com/DeepTMHMM")
        return False

def main():
    """Run DeepTMHMM on all ASFV proteins"""
    
    logger.info("=" * 60)
    logger.info("DEEPTMHMM PREDICTION")
    logger.info("=" * 60)
    
    protein_dir = Path("data/interim/proteins")
    protein_files = list(protein_dir.glob("*_sequences.fasta"))
    
    # Rate limit: 1 request per 10 seconds (free tier)
    for i, protein_file in enumerate(protein_files):
        logger.info(f"\nProcessing {i+1}/{len(protein_files)}: {protein_file.name}")
        
        # Submit to DeepTMHMM
        submit_deeptmhmm(protein_file)
        
        # Rate limit
        if i < len(protein_files) - 1:
            time.sleep(10)
    
    logger.info("\n✅ DeepTMHMM complete")

if __name__ == "__main__":
    main()
