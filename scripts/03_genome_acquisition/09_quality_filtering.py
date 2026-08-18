#!/usr/bin/env python3
"""
Section 3.3.2: Quality Filtering
Filters genomes by quality metrics (N50, completeness, contamination)
"""

import json
import logging
from pathlib import Path
from Bio import SeqIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_n50(genome_file):
    """Calculate N50 for a genome"""
    contig_lengths = []
    for record in SeqIO.parse(genome_file, "fasta"):
        contig_lengths.append(len(record.seq))
    
    if not contig_lengths:
        return 0
    
    contig_lengths.sort(reverse=True)
    total_length = sum(contig_lengths)
    half_length = total_length / 2
    
    running_sum = 0
    for length in contig_lengths:
        running_sum += length
        if running_sum >= half_length:
            return length
    return contig_lengths[-1] if contig_lengths else 0

def filter_genomes():
    """Filter genomes by quality metrics"""
    
    genome_dir = Path("data/raw/genomes")
    output_dir = Path("data/processed/genomes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Quality thresholds
    thresholds = {
        "min_n50": 100000,  # 100kb
        "min_completeness": 90.0,  # 90%
        "max_contamination": 5.0  # 5%
    }
    
    results = {}
    
    for gb_file in genome_dir.glob("*.gbff"):
        accession = gb_file.stem
        logger.info(f"Checking {accession}...")
        
        # Count contigs/sequences
        contigs = 0
        total_length = 0
        for record in SeqIO.parse(gb_file, "genbank"):
            contigs += 1
            total_length += len(record.seq)
        
        # Calculate N50 (using fasta version if available)
        fasta_file = genome_dir / f"{accession}.fasta"
        n50 = calculate_n50(fasta_file) if fasta_file.exists() else 0
        
        # Estimate completeness (simple metric: coverage of reference)
        # For ASFV, reference genome is ~170-190kb
        completeness = min(100, (total_length / 170000) * 100)
        
        # Simple contamination estimate (proportion of sequences < 1kb)
        small_contigs = 0
        for record in SeqIO.parse(gb_file, "genbank"):
            if len(record.seq) < 1000:
                small_contigs += 1
        contamination = (small_contigs / contigs * 100) if contigs > 0 else 0
        
        # Apply filters
        passed = (
            n50 >= thresholds["min_n50"] and
            completeness >= thresholds["min_completeness"] and
            contamination <= thresholds["max_contamination"]
        )
        
        results[accession] = {
            "accession": accession,
            "contigs": contigs,
            "total_length": total_length,
            "n50": n50,
            "completeness": round(completeness, 2),
            "contamination": round(contamination, 2),
            "passed": passed,
            "thresholds": thresholds
        }
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {status} (N50: {n50:,}, Completeness: {completeness:.1f}%, Contamination: {contamination:.1f}%)")
    
    # Save results
    output_file = output_dir / "quality_filter.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Quality filtering results saved to {output_file}")
    
    # Summary
    passed_count = sum(1 for r in results.values() if r["passed"])
    logger.info(f"\n📊 Summary: {passed_count}/{len(results)} genomes passed quality filters")

if __name__ == "__main__":
    filter_genomes()
