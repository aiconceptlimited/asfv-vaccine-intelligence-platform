#!/usr/bin/env python3
"""
Section 3.4.5: SignalP-6.0 via API
Uses DTU Health Tech's SignalP-6.0 web service
"""

import os
import sys
import json
import time
import logging
import requests
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def submit_signalp(protein_file, organism='eukaryota'):
    """
    Submit protein to SignalP-6.0 web service
    Note: This uses the free web API with rate limiting
    """
    
    # DTU Health Tech SignalP-6.0 API endpoint
    url = "https://services.healthtech.dtu.dk/api/v1/signalp"
    
    # Read protein sequences
    with open(protein_file, 'r') as f:
        sequences = f.read()
    
    # Prepare request
    payload = {
        'sequence': sequences,
        'organism': organism,  # eukaryota, gram_positive, gram_negative
        'format': 'json'
    }
    
    try:
        logger.info(f"Submitting {Path(protein_file).name} to SignalP-6.0...")
        
        # Submit job
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Save results
        output_dir = Path("data/processed/signalp")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{Path(protein_file).stem}_signalp.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Parse results
        if 'predictions' in result:
            signal_peptides = 0
            for pred in result['predictions']:
                if pred.get('signal_peptide', False):
                    signal_peptides += 1
            
            logger.info(f"✅ Found {signal_peptides} signal peptides")
            logger.info(f"   Results saved to {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SignalP-6.0 API failed: {e}")
        logger.info("   Please use web interface: https://services.healthtech.dtu.dk/services/SignalP-6.0/")
        return False

def main():
    """Run SignalP-6.0 on all ASFV proteins"""
    
    logger.info("=" * 60)
    logger.info("SIGNALP-6.0 PREDICTION")
    logger.info("=" * 60)
    
    protein_dir = Path("data/interim/proteins")
    protein_files = list(protein_dir.glob("*_sequences.fasta"))
    
    # Rate limit: 1 request per 5 seconds (free tier)
    for i, protein_file in enumerate(protein_files):
        logger.info(f"\nProcessing {i+1}/{len(protein_files)}: {protein_file.name}")
        
        # Submit to SignalP
        submit_signalp(protein_file)
        
        # Rate limit
        if i < len(protein_files) - 1:
            time.sleep(5)
    
    logger.info("\n✅ SignalP-6.0 complete")
    logger.info("⚠️  NOTE: This uses the free API which has rate limits")
    logger.info("   For large datasets, use local installation or web server")

if __name__ == "__main__":
    main()
