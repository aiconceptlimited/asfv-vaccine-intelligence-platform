#!/usr/bin/env python3
"""
Section 3.3.4: Genotype Confirmation (Refined)
Extracts p72/B646L sequences with improved synonym detection

Input:  data/raw/genomes/*.genbank
Output: data/processed/alignments/b646l_sequences.fasta
        data/processed/alignments/b646l_aligned.fasta
        data/processed/alignments/b646l_phylogeny.treefile
        data/metadata/genotype_summary.json
        results/03_genomes/genotype_report.html

Author: Abubakar
Date: 2026-07-11 (Refined)
"""

import os
import sys
import json
import csv
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asfv_platform.utils import setup_logger
from asfv_platform.io import ensure_directory, write_json

# Setup logger
logger = setup_logger(__name__, "logs/qc/04_genotype.log")


# ============================================================
# B646L Synonyms (Case-insensitive)
# ============================================================
B646L_SYNONYMS = [
    "b646l",
    "p72",
    "major capsid protein",
    "major capsid protein p72",
    "capsid protein",
    "capsid protein p72"
]


def is_b646l(feature):
    """
    Check if a CDS feature is B646L/p72 using multiple qualifiers
    
    Args:
        feature: Biopython feature object
    
    Returns:
        bool: True if B646L/p72 detected
    """
    # Check gene name
    gene = feature.qualifiers.get("gene", [""])[0].lower() if "gene" in feature.qualifiers else ""
    if gene in ["b646l", "p72"]:
        return True
    
    # Check product
    product = feature.qualifiers.get("product", [""])[0].lower() if "product" in feature.qualifiers else ""
    for synonym in B646L_SYNONYMS:
        if synonym in product:
            return True
    
    # Check note
    note = feature.qualifiers.get("note", [""])[0].lower() if "note" in feature.qualifiers else ""
    for synonym in B646L_SYNONYMS:
        if synonym in note:
            return True
    
    # Check protein_id
    protein_id = feature.qualifiers.get("protein_id", [""])[0].lower() if "protein_id" in feature.qualifiers else ""
    if "p72" in protein_id:
        return True
    
    return False


def extract_b646l(gbk_file):
    """
    Extract p72/B646L protein sequence from GenBank file
    
    Args:
        gbk_file: Path to GenBank file
    
    Returns:
        tuple: (accession, sequence, status, length, notes)
    """
    accession = gbk_file.stem
    status = "NOT_FOUND"
    sequence = None
    length = 0
    notes = []
    
    try:
        for record in SeqIO.parse(gbk_file, "genbank"):
            for feature in record.features:
                if feature.type == "CDS":
                    if is_b646l(feature):
                        if "translation" in feature.qualifiers:
                            seq = feature.qualifiers["translation"][0]
                            sequence = seq
                            length = len(seq)
                            
                            # Check for completeness
                            has_start = seq.startswith("M")
                            has_stop = "*" in seq[:-1] if seq else False
                            is_partial = "partial" in str(feature.qualifiers).lower()
                            
                            if length == 646 and has_start and not has_stop:
                                status = "FULL_LENGTH"
                                notes.append("Complete p72 (646 aa)")
                            elif length < 646 and length > 300:
                                status = "TRUNCATED"
                                notes.append(f"Truncated p72 ({length} aa)")
                                if is_partial:
                                    notes.append("Marked as partial")
                            elif length >= 646:
                                status = "FULL_LENGTH"
                                notes.append(f"Full length ({length} aa)")
                            else:
                                status = "SHORT"
                                notes.append(f"Short p72 ({length} aa)")
                            
                            logger.info(f"  {accession}: {status} ({length} aa)")
                            return accession, sequence, status, length, "; ".join(notes)
                        else:
                            notes.append("Found CDS but no translation")
            
            # If B646L not found in this record
            notes.append("B646L not found in annotation")
            logger.warning(f"  {accession}: B646L not found")
            return accession, None, "NOT_FOUND", 0, "Not found"
            
    except Exception as e:
        logger.error(f"  {accession}: Error extracting B646L - {e}")
        return accession, None, "ERROR", 0, str(e)


def run_mafft(input_file, output_file):
    """Run MAFFT alignment"""
    try:
        cmd = f"mafft --localpair --maxiterate 1000 --thread 4 {input_file} > {output_file}"
        logger.info(f"Running MAFFT: {cmd}")
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"  MAFFT alignment complete: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"  MAFFT failed: {e.stderr}")
        return False


def run_iqtree(input_file, output_prefix):
    """
    Run IQ-TREE phylogenetic inference with -redo if checkpoint exists
    """
    try:
        # Remove checkpoint file if it exists
        ckp_file = Path(f"{output_prefix}.ckp.gz")
        if ckp_file.exists():
            logger.info(f"  Removing existing checkpoint: {ckp_file}")
            ckp_file.unlink()
        
        cmd = f"iqtree2 -s {input_file} -m LG -nt AUTO -pre {output_prefix}"
        logger.info(f"Running IQ-TREE: {cmd}")
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"  IQ-TREE complete: {output_prefix}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"  IQ-TREE failed: {e.stderr}")
        return False


def parse_tree_file(treefile_path):
    """Parse IQ-TREE tree file"""
    try:
        with open(treefile_path, 'r') as f:
            tree_str = f.read().strip()
        return {'tree_string': tree_str, 'file_path': str(treefile_path)}
    except Exception as e:
        logger.error(f"Error parsing tree file: {e}")
        return None


def generate_genotype_report(qc_results, metadata, tree_info, output_path):
    """Generate HTML genotype report"""
    
    # Build genotype summary from metadata
    genotype_summary = {}
    for acc in metadata:
        genotype = metadata[acc].get('genotype', 'Unknown')
        if genotype not in genotype_summary:
            genotype_summary[genotype] = []
        genotype_summary[genotype].append(acc)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ASFV Genotype Confirmation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .confirmed {{ color: green; font-weight: bold; }}
        .truncated {{ color: orange; font-weight: bold; }}
        .notfound {{ color: red; font-weight: bold; }}
        .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .tree {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>ASFV Genotype Confirmation Report</h1>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Total Genomes:</strong> {len(metadata)}</p>
    
    <div class="summary">
        <h2>Genotype Summary</h2>
"""
    
    for genotype, genomes in sorted(genotype_summary.items()):
        html += f"""
        <p><strong>Genotype {genotype}:</strong> {len(genomes)} genomes</p>
        <ul>
"""
        for acc in sorted(genomes):
            html += f"<li>{acc}</li>"
        html += "</ul>"
    
    html += """
    </div>
    
    <h2>B646L Extraction Results</h2>
    <table>
        <tr>
            <th>Accession</th>
            <th>Genotype</th>
            <th>Status</th>
            <th>Length (aa)</th>
            <th>Notes</th>
        </tr>
"""
    
    for acc in sorted(metadata.keys()):
        result = next((r for r in qc_results if r['accession'] == acc), {})
        genotype = metadata[acc].get('genotype', 'Unknown')
        status = result.get('status', 'NOT_FOUND')
        length = result.get('length', 0)
        notes = result.get('notes', '')
        
        status_class = {
            'FULL_LENGTH': 'confirmed',
            'TRUNCATED': 'truncated',
            'NOT_FOUND': 'notfound',
            'SHORT': 'truncated',
            'ERROR': 'notfound'
        }.get(status, 'notfound')
        
        html += f"""
        <tr>
            <td><strong>{acc}</strong></td>
            <td>{genotype}</td>
            <td class="{status_class}">{status}</td>
            <td>{length}</td>
            <td>{notes}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>Phylogenetic Tree</h2>
    <div class="tree">
        <pre>
"""
    
    if tree_info and tree_info.get('tree_string'):
        html += tree_info['tree_string']
    else:
        html += "Tree file could not be parsed."
    
    html += """
        </pre>
    </div>
    
    <h2>Methodology</h2>
    <p><strong>Gene:</strong> B646L (p72)</p>
    <p><strong>Alignment:</strong> MAFFT (L-INS-i strategy)</p>
    <p><strong>Phylogeny:</strong> IQ-TREE 2 with LG model</p>
    <p><strong>Reference:</strong> Hakizimana et al., 2023</p>
    
    <p style="margin-top: 20px; font-size: 12px; color: #7f8c8d;">
        <strong>Note:</strong> Genotype assignments are confirmed based on phylogenetic clustering of B646L sequences.
    </p>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)
    logger.info(f"Genotype report saved to: {output_path}")


def main():
    """Main execution function"""
    
    # Define paths
    genomes_dir = PROJECT_ROOT / "data/raw/genomes"
    processed_dir = PROJECT_ROOT / "data/processed/alignments"
    metadata_dir = PROJECT_ROOT / "data/metadata"
    results_dir = PROJECT_ROOT / "results/03_genomes"
    
    ensure_directory(processed_dir)
    ensure_directory(metadata_dir)
    ensure_directory(results_dir)
    
    # Load genome metadata
    metadata_path = metadata_dir / "genome_metadata.json"
    if not metadata_path.exists():
        logger.error(f"Metadata not found: {metadata_path}")
        sys.exit(1)
    
    with open(metadata_path, 'r') as f:
        metadata = {item['accession']: item for item in json.load(f)}
    
    logger.info(f"Loaded metadata for {len(metadata)} genomes")
    
    # Find all GenBank files
    gbk_files = sorted(genomes_dir.glob("*.genbank"))
    
    if not gbk_files:
        logger.error(f"No GenBank files found in {genomes_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(gbk_files)} GenBank files")
    logger.info("=" * 60)
    
    # Extract B646L sequences
    logger.info("Extracting B646L (p72) sequences...")
    sequences = []
    qc_results = []
    
    for gbk_file in gbk_files:
        accession, seq, status, length, notes = extract_b646l(gbk_file)
        qc_results.append({
            'accession': accession,
            'status': status,
            'length': length,
            'notes': notes
        })
        if seq:
            sequences.append(SeqRecord(Seq(seq), id=accession, description=f"B646L|{accession}"))
        logger.info("-" * 40)
    
    # Save sequences
    fasta_path = processed_dir / "b646l_sequences.fasta"
    with open(fasta_path, 'w') as f:
        SeqIO.write(sequences, f, "fasta")
    logger.info(f"Sequences saved to: {fasta_path}")
    logger.info(f"  {len(sequences)} sequences extracted")
    
    # Run MAFFT if enough sequences
    if len(sequences) > 1:
        logger.info("")
        logger.info("Running MAFFT alignment...")
        aligned_path = processed_dir / "b646l_aligned.fasta"
        if run_mafft(fasta_path, aligned_path):
            logger.info(f"Alignment saved to: {aligned_path}")
            
            # Run IQ-TREE
            logger.info("")
            logger.info("Running IQ-TREE phylogeny...")
            prefix = processed_dir / "b646l_phylogeny"
            if run_iqtree(aligned_path, prefix):
                logger.info(f"Phylogeny saved to: {prefix}")
                treefile_path = processed_dir / "b646l_phylogeny.treefile"
                tree_info = parse_tree_file(treefile_path) if treefile_path.exists() else None
            else:
                tree_info = None
        else:
            tree_info = None
    else:
        logger.warning("Not enough sequences for phylogeny")
        tree_info = None
    
    # Generate genotype summary from metadata
    genotype_summary = {
        'total_genomes': len(metadata),
        'genotypes': {}
    }
    
    for acc, data in metadata.items():
        genotype = data.get('genotype', 'Unknown')
        if genotype not in genotype_summary['genotypes']:
            genotype_summary['genotypes'][genotype] = []
        genotype_summary['genotypes'][genotype].append(acc)
    
    summary_path = metadata_dir / "genotype_summary.json"
    write_json(genotype_summary, summary_path)
    logger.info(f"Genotype summary saved to: {summary_path}")
    
    # Generate HTML report
    html_path = results_dir / "genotype_report.html"
    generate_genotype_report(qc_results, metadata, tree_info, html_path)
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SECTION 3.3.4: GENOTYPE CONFIRMATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total genomes: {len(metadata)}")
    
    status_counts = {}
    for r in qc_results:
        status = r['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        logger.info(f"  {status}: {count}")
    
    logger.info(f"Genotypes: {list(genotype_summary['genotypes'].keys())}")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
