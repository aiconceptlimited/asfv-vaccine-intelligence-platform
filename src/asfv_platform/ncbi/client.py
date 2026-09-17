#!/usr/bin/env python3
"""
NCBI Client Module
Handles all communication with NCBI Entrez
"""

import time
import logging
from Bio import Entrez, SeqIO

logger = logging.getLogger(__name__)

class NCBIClientError(Exception):
    """Custom exception for NCBI client errors"""
    pass

def download_genbank_record(accession, email, retries=3, delay=1):
    """Download GenBank record with retries"""
    Entrez.email = email
    
    for attempt in range(retries):
        try:
            handle = Entrez.efetch(db="nucleotide", id=accession, rettype="gb", retmode="text")
            record = SeqIO.read(handle, "genbank")
            handle.close()
            
            if record is None:
                raise NCBIClientError(f"Empty record returned for {accession}")
            return record
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed for {accession}: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise NCBIClientError(f"Failed to download {accession}: {e}")

def download_fasta_record(accession, email, retries=3, delay=1):
    """Download FASTA record with retries"""
    Entrez.email = email
    
    for attempt in range(retries):
        try:
            handle = Entrez.efetch(db="nucleotide", id=accession, rettype="fasta", retmode="text")
            record = SeqIO.read(handle, "fasta")
            handle.close()
            
            if record is None:
                raise NCBIClientError(f"Empty FASTA returned for {accession}")
            return record
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed for {accession}: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise NCBIClientError(f"Failed to download FASTA for {accession}: {e}")

def extract_metadata(record):
    """Extract metadata from GenBank record"""
    return {
        'accession': record.id.split('.')[0],
        'accession_version': record.id,
        'length': len(record.seq),
        'gc_content': round((record.seq.count('G') + record.seq.count('C')) / len(record.seq) * 100, 2),
        'ambiguous': record.seq.count('N'),
        'cds_count': len([f for f in record.features if f.type == "CDS"]),
        'assembly_status': "Complete" if "complete" in str(record.annotations).lower() else "Unknown"
    }
