#!/usr/bin/env python3
"""NCBI communication utilities"""
from .client import download_genbank_record, download_fasta_record, extract_metadata, NCBIClientError
