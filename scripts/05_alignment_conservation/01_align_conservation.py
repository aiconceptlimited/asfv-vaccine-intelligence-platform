#!/usr/bin/env python3
"""
Section 3.5: Multiple Sequence Alignment and Conservation Analysis
Performs MAFFT alignment and calculates conservation for each target protein

Input:  data/interim/proteins/*.fasta
Output: data/processed/alignments/*.aligned.fasta
        data/processed/alignments/*_conservation.json
        data/processed/conservation/conservation_summary.csv
        data/processed/conservation/conservation_report.json
        results/05_alignments/alignment_report.html

Author: Abubakar
Date: 2026-07-11
"""

import os
import sys
import json
import csv
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from collections import Counter
from Bio import SeqIO, AlignIO
from Bio.Align import MultipleSeqAlignment
import numpy as np

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asfv_platform.utils import setup_logger
from asfv_platform.io import ensure_directory, write_json

# Setup logger
logger = setup_logger(__name__, "logs/analysis/05_alignment.log")


# ============================================================
# Target Proteins
# ============================================================
TARGET_PROTEINS = [
    {'gene': 'B646L', 'protein': 'p72'},
    {'gene': 'CP204L', 'protein': 'p30'},
    {'gene': 'E183L', 'protein': 'p54'},
    {'gene': 'EP402R', 'protein': 'CD2v'},
    {'gene': 'CP2475L', 'protein': 'pp220'},
    {'gene': 'CP312R', 'protein': 'pCP312R'}
]


# ============================================================
# Alignment Functions
# ============================================================
def run_mafft(input_file, output_file):
    """
    Run MAFFT alignment with L-INS-i strategy
    """
    try:
        cmd = f"mafft --localpair --maxiterate 1000 --thread 4 {input_file} > {output_file}"
        logger.info(f"Running MAFFT: {cmd}")
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        logger.info(f"  Alignment complete: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"  MAFFT failed: {e.stderr}")
        return False


def calculate_conservation(alignment_file):
    """
    Calculate residue-level conservation from alignment
    
    Returns:
        dict: Conservation metrics per position
    """
    alignment = AlignIO.read(alignment_file, "fasta")
    seq_len = alignment.get_alignment_length()
    
    conservation = []
    
    for pos in range(seq_len):
        column = alignment[:, pos]
        residues = [c for c in column if c != '-']
        total = len(column)
        gaps = total - len(residues)
        
        if residues:
            freq = Counter(residues)
            total_residues = len(residues)
            consensus = freq.most_common(1)[0]
            entropy = -sum([(c/total_residues) * np.log(c/total_residues) for c in freq.values()])
            
            conservation.append({
                'position': pos + 1,
                'consensus': consensus[0],
                'frequency': round(consensus[1] / total_residues * 100, 2),
                'entropy': round(entropy, 4),
                'variants': len(freq),
                'gap_frequency': round(gaps / total * 100, 2),
                'residue_count': total_residues
            })
        else:
            conservation.append({
                'position': pos + 1,
                'consensus': '-',
                'frequency': 0,
                'entropy': 0,
                'variants': 0,
                'gap_frequency': 100,
                'residue_count': 0
            })
    
    return conservation


def calculate_alignment_stats(alignment_file):
    """
    Calculate alignment statistics
    """
    alignment = AlignIO.read(alignment_file, "fasta")
    seq_len = alignment.get_alignment_length()
    num_seqs = len(alignment)
    
    # Calculate pairwise identity (simplified)
    sequences = [str(record.seq) for record in alignment]
    
    # Calculate gap statistics
    gap_counts = []
    seq_lengths = []
    for seq in sequences:
        gap_counts.append(seq.count('-'))
        seq_lengths.append(len(seq) - seq.count('-'))
    
    return {
        'num_sequences': num_seqs,
        'alignment_length': seq_len,
        'mean_sequence_length': round(np.mean(seq_lengths), 1),
        'min_sequence_length': min(seq_lengths),
        'max_sequence_length': max(seq_lengths),
        'mean_gaps': round(np.mean(gap_counts), 1),
        'max_gaps': max(gap_counts),
        'sequences': [str(record.id) for record in alignment]
    }


def classify_protein_status(protein_name, accession, length, expected_length):
    """
    Classify protein status based on length
    """
    if length == 0:
        return 'NOT_FOUND'
    elif length >= expected_length * 0.90:
        return 'FULL_LENGTH'
    elif length >= expected_length * 0.50:
        return 'TRUNCATED'
    else:
        return 'SEVERELY_TRUNCATED'


def generate_conservation_report(protein_data, output_path):
    """
    Generate HTML conservation report
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Conservation Report - {protein_data['protein']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 0 20px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .conserved {{ color: green; }}
        .variable {{ color: orange; }}
        .highly-variable {{ color: red; }}
    </style>
</head>
<body>
    <h1>Conservation Analysis: {protein_data['protein']} ({protein_data['gene']})</h1>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="metric">
            <div class="metric-value">{protein_data['stats']['num_sequences']}</div>
            <div>Sequences</div>
        </div>
        <div class="metric">
            <div class="metric-value">{protein_data['stats']['alignment_length']}</div>
            <div>Alignment Length</div>
        </div>
        <div class="metric">
            <div class="metric-value">{protein_data['stats']['mean_sequence_length']:.0f}</div>
            <div>Mean Length (aa)</div>
        </div>
    </div>
    
    <h2>Sequence Status</h2>
    <table>
        <tr>
            <th>Accession</th>
            <th>Length (aa)</th>
            <th>Status</th>
        </tr>
"""
    
    for seq in protein_data['sequences']:
        status_class = {
            'FULL_LENGTH': 'conserved',
            'TRUNCATED': 'variable',
            'SEVERELY_TRUNCATED': 'highly-variable',
            'NOT_FOUND': 'highly-variable'
        }.get(seq['status'], '')
        
        html += f"""
        <tr>
            <td><strong>{seq['accession']}</strong></td>
            <td>{seq['length']}</td>
            <td class="{status_class}">{seq['status']}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>Conservation Statistics</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        <tr><td>Mean Conservation</td><td>{:.1f}%</td></tr>
        <tr><td>Median Conservation</td><td>{:.1f}%</td></tr>
        <tr><td>Min Conservation</td><td>{:.1f}%</td></tr>
        <tr><td>Max Conservation</td><td>{:.1f}%</td></tr>
        <tr><td>Highly Conserved Positions (>90%)</td><td>{}</td></tr>
        <tr><td>Variable Positions (50-90%)</td><td>{}</td></tr>
        <tr><td>Highly Variable Positions (<50%)</td><td>{}</td></tr>
    </table>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)
    logger.info(f"  Report saved: {output_path}")


def main():
    """Main execution function"""
    
    # Define paths
    proteins_dir = PROJECT_ROOT / "data/interim/proteins"
    alignments_dir = PROJECT_ROOT / "data/processed/alignments"
    conservation_dir = PROJECT_ROOT / "data/processed/conservation"
    results_dir = PROJECT_ROOT / "results/05_alignments"
    
    ensure_directory(alignments_dir)
    ensure_directory(conservation_dir)
    ensure_directory(results_dir)
    
    logger.info("=" * 60)
    logger.info("SECTION 3.5: ALIGNMENT & CONSERVATION ANALYSIS")
    logger.info("=" * 60)
    
    all_summary = []
    
    for target in TARGET_PROTEINS:
        gene = target['gene']
        protein = target['protein']
        
        input_file = proteins_dir / f"{gene}_{protein}_sequences.fasta"
        
        if not input_file.exists():
            logger.warning(f"Input file not found: {input_file}")
            continue
        
        logger.info(f"\nProcessing {protein} ({gene})...")
        
        # Count sequences
        sequences = list(SeqIO.parse(input_file, "fasta"))
        logger.info(f"  Sequences: {len(sequences)}")
        
        # Run MAFFT alignment
        aligned_file = alignments_dir / f"{gene}_{protein}_aligned.fasta"
        if run_mafft(input_file, aligned_file):
            logger.info(f"  Alignment saved: {aligned_file}")
        else:
            continue
        
        # Calculate conservation
        conservation = calculate_conservation(aligned_file)
        
        # Save conservation JSON
        cons_json = alignments_dir / f"{gene}_{protein}_conservation.json"
        write_json(conservation, cons_json)
        logger.info(f"  Conservation saved: {cons_json}")
        
        # Calculate alignment stats
        stats = calculate_alignment_stats(aligned_file)
        
        # Determine sequence statuses
        seq_statuses = []
        for record in SeqIO.parse(input_file, "fasta"):
            accession = record.id.split('|')[0]
            length = len(str(record.seq))
            expected = 646 if gene == 'B646L' else 204 if gene == 'CP204L' else 183 if gene == 'E183L' else 402 if gene == 'EP402R' else 2475 if gene == 'CP2475L' else 312
            status = classify_protein_status(protein, accession, length, expected)
            seq_statuses.append({
                'accession': accession,
                'length': length,
                'status': status
            })
        
        # Calculate conservation summary
        cons_values = [c['frequency'] for c in conservation]
        highly_conserved = sum(1 for c in conservation if c['frequency'] >= 90)
        variable = sum(1 for c in conservation if 50 <= c['frequency'] < 90)
        highly_variable = sum(1 for c in conservation if c['frequency'] < 50 and c['frequency'] > 0)
        
        # Store summary
        protein_summary = {
            'gene': gene,
            'protein': protein,
            'num_sequences': stats['num_sequences'],
            'alignment_length': stats['alignment_length'],
            'mean_conservation': round(np.mean(cons_values), 1) if cons_values else 0,
            'highly_conserved': highly_conserved,
            'variable': variable,
            'highly_variable': highly_variable,
            'sequences': seq_statuses,
            'stats': stats
        }
        all_summary.append(protein_summary)
        
        # Generate HTML report
        report_path = results_dir / f"{gene}_{protein}_conservation_report.html"
        generate_conservation_report(protein_summary, report_path)
        
        logger.info(f"  Completed: {protein} ({gene})")
    
    # Save summary CSV
    summary_csv = conservation_dir / "conservation_summary.csv"
    with open(summary_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['gene', 'protein', 'num_sequences', 'alignment_length', 'mean_conservation', 'highly_conserved', 'variable', 'highly_variable'])
        writer.writeheader()
        for s in all_summary:
            writer.writerow({
                'gene': s['gene'],
                'protein': s['protein'],
                'num_sequences': s['num_sequences'],
                'alignment_length': s['alignment_length'],
                'mean_conservation': s['mean_conservation'],
                'highly_conserved': s['highly_conserved'],
                'variable': s['variable'],
                'highly_variable': s['highly_variable']
            })
    logger.info(f"\nSummary CSV saved: {summary_csv}")
    
    # Save JSON report
    report_json = conservation_dir / "conservation_report.json"
    write_json(all_summary, report_json)
    logger.info(f"Summary JSON saved: {report_json}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SECTION 3.5: ALIGNMENT & CONSERVATION COMPLETE")
    logger.info("=" * 60)
    for s in all_summary:
        logger.info(f"  {s['protein']} ({s['gene']}): {s['num_sequences']} seqs, alignment {s['alignment_length']} aa, mean conservation {s['mean_conservation']}%")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
