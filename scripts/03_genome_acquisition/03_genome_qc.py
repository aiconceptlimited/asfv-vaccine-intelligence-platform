#!/usr/bin/env python3
"""
Section 3.3.3: Genome Quality Control (Final)
Evaluates genome completeness, sequence integrity, and annotation quality

Technical QC (PASS/FAIL):
- Record parseable
- Assembly status: Complete
- Valid nucleotide sequence (ACGTN + IUPAC codes: R,Y,S,W,K,M,B,D,H,V)
- No internal gaps
- Genome length ≥ 100,000 bp

Biological Observations (Informational):
- CDS count
- Genome length (recorded, no PASS/FAIL)
- Ambiguous N count
- IUPAC ambiguity codes count

Input:  data/raw/genomes/*.genbank
        data/metadata/genome_metadata.csv
Output: data/metadata/genome_qc_results.json
        data/metadata/genome_qc_summary.csv
        results/03_genomes/qc_report.html

Author: Abubakar
Date: 2026-07-11
"""

import os
import sys
import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from Bio import SeqIO

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asfv_platform.utils import setup_logger
from asfv_platform.io import ensure_directory, write_json

# Setup logger
logger = setup_logger(__name__, "logs/qc/03_qc.log")


# ============================================================
# Valid IUPAC Nucleotide Codes
# ============================================================
# Full IUPAC nucleotide alphabet
# A, C, G, T - Standard bases
# N - Any base
# R, Y, S, W, K, M - Ambiguity codes
# B, D, H, V - Complement ambiguity codes
IUPAC_CODES = set('ACGTNRYSWKMBDHVacgtnryswkmbdhv')

QC_THRESHOLDS = {
    'ambiguous': {
        'pass': 1000,  # N count threshold
    },
    'gaps': {
        'pass': 0
    },
    'length': {
        'min': 100000
    }
}


# ============================================================
# QC Functions
# ============================================================
def check_genome_record(gbk_file):
    """
    Perform QC checks on a single GenBank file
    
    Technical checks determine PASS/FAIL.
    Biological observations are recorded as notes.
    
    Args:
        gbk_file: Path to GenBank file
    
    Returns:
        dict: QC results
    """
    accession = gbk_file.stem
    result = {
        'accession': accession,
        'file_path': str(gbk_file),
        'checks': {},
        'observations': {},
        'notes': [],
        'status': 'PASS'
    }
    
    try:
        for record in SeqIO.parse(gbk_file, "genbank"):
            seq = str(record.seq)
            length = len(seq)
            
            # ============================================================
            # Technical QC (PASS/FAIL)
            # ============================================================
            
            # 1. Record parseable (implicit - if we got here, it's parseable)
            result['checks']['parseable'] = {
                'value': True,
                'passed': True
            }
            
            # 2. Assembly status
            assembly_status = "Complete" if "complete" in str(record.annotations).lower() else "Unknown"
            assembly_pass = assembly_status == "Complete"
            result['checks']['assembly_status'] = {
                'value': assembly_status,
                'expected': 'Complete',
                'passed': assembly_pass
            }
            if not assembly_pass:
                result['notes'].append(f"Assembly status: {assembly_status}")
            
            # 3. Valid nucleotide sequence (accept IUPAC codes)
            invalid_chars = set(seq) - IUPAC_CODES
            invalid_pass = len(invalid_chars) == 0
            result['checks']['valid_sequence'] = {
                'value': 'Valid' if invalid_pass else f"Invalid characters: {invalid_chars}",
                'expected': 'Valid (ACGTN + IUPAC codes)',
                'passed': invalid_pass
            }
            if not invalid_pass:
                result['notes'].append(f"Invalid characters: {invalid_chars}")
            
            # 4. Ambiguous nucleotides (N count)
            n_count = seq.count('N')
            n_pass = n_count <= QC_THRESHOLDS['ambiguous']['pass']
            result['checks']['ambiguous_nucleotides'] = {
                'value': n_count,
                'expected': f"≤ {QC_THRESHOLDS['ambiguous']['pass']}",
                'passed': n_pass
            }
            if not n_pass:
                result['notes'].append(f"High N content: {n_count}")
            
            # 5. Internal gaps
            gap_count = seq.count('-')
            gaps_pass = gap_count == QC_THRESHOLDS['gaps']['pass']
            result['checks']['internal_gaps'] = {
                'value': gap_count,
                'expected': '0',
                'passed': gaps_pass
            }
            if not gaps_pass:
                result['notes'].append(f"Internal gaps found: {gap_count}")
            
            # 6. Genome length (technical check: not too small)
            length_pass = length >= QC_THRESHOLDS['length']['min']
            result['checks']['genome_length'] = {
                'value': length,
                'expected': f"≥ {QC_THRESHOLDS['length']['min']:,} bp",
                'passed': length_pass
            }
            if not length_pass:
                result['notes'].append(f"Very short genome: {length:,} bp")
            
            # ============================================================
            # Biological Observations (Informational)
            # ============================================================
            
            # 7. CDS count (recorded as observation, not PASS/FAIL)
            cds_count = len([f for f in record.features if f.type == "CDS"])
            result['observations']['cds_count'] = cds_count
            
            # 8. GC content
            gc = (seq.count('G') + seq.count('C')) / length * 100 if length > 0 else 0
            result['observations']['gc_content'] = round(gc, 2)
            
            # 9. Genome length (also recorded as observation)
            result['observations']['genome_length'] = length
            
            # 10. Ambiguous N count (observation)
            result['observations']['n_count'] = n_count
            
            # 11. Count IUPAC ambiguity codes (R,Y,S,W,K,M,B,D,H,V)
            iupac_ambiguity_codes = set('RYSWKMBDHVrys wkmbdhv')
            iupac_count = sum(1 for char in seq if char.upper() in iupac_ambiguity_codes)
            result['observations']['iupac_ambiguity_count'] = iupac_count
            
            # Determine overall status
            # FAIL only if any technical check failed
            all_checks_passed = all(check.get('passed', False) for check in result['checks'].values())
            result['status'] = 'PASS' if all_checks_passed else 'FAIL'
            
            break  # Only process first record
    
    except Exception as e:
        logger.error(f"Error processing {gbk_file}: {e}")
        result['status'] = 'FAIL'
        result['notes'].append(f"Error: {str(e)}")
    
    return result


def generate_qc_summary(qc_results):
    """
    Generate summary statistics from QC results
    
    Args:
        qc_results: List of QC result dictionaries
    
    Returns:
        dict: Summary statistics
    """
    total = len(qc_results)
    passed = sum(1 for r in qc_results if r['status'] == 'PASS')
    failed = sum(1 for r in qc_results if r['status'] == 'FAIL')
    
    # Collect notes and observations
    all_notes = []
    cds_counts = []
    genome_lengths = []
    iupac_counts = []
    for r in qc_results:
        all_notes.extend(r.get('notes', []))
        if 'cds_count' in r.get('observations', {}):
            cds_counts.append(r['observations']['cds_count'])
        if 'genome_length' in r.get('observations', {}):
            genome_lengths.append(r['observations']['genome_length'])
        if 'iupac_ambiguity_count' in r.get('observations', {}):
            iupac_counts.append(r['observations']['iupac_ambiguity_count'])
    
    return {
        'total_genomes': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': round(passed / total * 100, 1) if total > 0 else 0,
        'all_notes': all_notes,
        'cds_counts': cds_counts,
        'genome_lengths': genome_lengths,
        'iupac_counts': iupac_counts
    }


def generate_html_report(qc_results, summary, output_path):
    """
    Generate HTML QC report
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ASFV Genome QC Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #34495e; margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 0 20px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .note {{ color: #856404; background-color: #fff3cd; padding: 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>ASFV Genome Quality Control Report</h1>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Genomes:</strong> {summary['total_genomes']}</p>
        <div class="metric">
            <div class="metric-value" style="color: green;">{summary['passed']}</div>
            <div>PASS</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: red;">{summary['failed']}</div>
            <div>FAIL</div>
        </div>
        <div class="metric">
            <div class="metric-value">{summary['pass_rate']}%</div>
            <div>Pass Rate</div>
        </div>
    </div>
    
    <h2>Technical QC Results</h2>
    <table>
        <tr>
            <th>Accession</th>
            <th>Assembly</th>
            <th>Sequence Valid</th>
            <th>N Count</th>
            <th>Gaps</th>
            <th>Length (bp)</th>
            <th>Status</th>
        </tr>
"""
    
    for r in qc_results:
        checks = r.get('checks', {})
        assembly = checks.get('assembly_status', {}).get('value', 'N/A')
        valid_seq = checks.get('valid_sequence', {}).get('value', 'N/A')
        n_count = checks.get('ambiguous_nucleotides', {}).get('value', 'N/A')
        gaps = checks.get('internal_gaps', {}).get('value', 'N/A')
        length = checks.get('genome_length', {}).get('value', 'N/A')
        
        status_class = {
            'PASS': 'pass',
            'FAIL': 'fail'
        }.get(r['status'], '')
        
        html += f"""
        <tr>
            <td><strong>{r['accession']}</strong></td>
            <td>{assembly}</td>
            <td>{valid_seq}</td>
            <td>{n_count}</td>
            <td>{gaps}</td>
            <td>{length:,}</td>
            <td class="{status_class}">{r['status']}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>Biological Observations</h2>
    <table>
        <tr>
            <th>Accession</th>
            <th>CDS Count</th>
            <th>GC %</th>
            <th>Genome Length (bp)</th>
            <th>IUPAC Ambiguity</th>
        </tr>
"""
    
    for r in qc_results:
        obs = r.get('observations', {})
        cds = obs.get('cds_count', 'N/A')
        gc = obs.get('gc_content', 'N/A')
        length = obs.get('genome_length', 'N/A')
        iupac = obs.get('iupac_ambiguity_count', 'N/A')
        
        html += f"""
        <tr>
            <td><strong>{r['accession']}</strong></td>
            <td>{cds}</td>
            <td>{gc}</td>
            <td>{length:,}</td>
            <td>{iupac}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>Notes</h2>
"""
    
    if summary['all_notes']:
        html += "<ul>"
        for note in summary['all_notes']:
            html += f"<li class='note'>{note}</li>"
        html += "</ul>"
    else:
        html += "<p style='color: green;'>✅ No issues found.</p>"
    
    html += """
    <h2>QC Criteria (Technical)</h2>
    <table>
        <tr><th>Criteria</th><th>PASS</th><th>FAIL</th></tr>
        <tr><td>Record Parseable</td><td>Yes</td><td>No</td></tr>
        <tr><td>Assembly Status</td><td>Complete</td><td>Not Complete</td></tr>
        <tr><td>Valid Sequence</td><td>ACGTN + IUPAC codes</td><td>Invalid characters</td></tr>
        <tr><td>Internal Gaps</td><td>0</td><td>&gt; 0</td></tr>
        <tr><td>Genome Length</td><td>≥ 100,000 bp</td><td>&lt; 100,000 bp</td></tr>
    </table>
    <p style="margin-top: 20px; font-size: 12px; color: #7f8c8d;">
        <strong>Note:</strong> CDS count, genome length variation, and IUPAC ambiguity codes are reported as observations, not QC criteria.
    </p>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)
    logger.info(f"HTML report saved to: {output_path}")


def main():
    """Main execution function"""
    
    # Define paths
    genomes_dir = PROJECT_ROOT / "data/raw/genomes"
    metadata_dir = PROJECT_ROOT / "data/metadata"
    results_dir = PROJECT_ROOT / "results/03_genomes"
    
    ensure_directory(metadata_dir)
    ensure_directory(results_dir)
    
    # Find all GenBank files
    gbk_files = sorted(genomes_dir.glob("*.genbank"))
    
    if not gbk_files:
        logger.error(f"No GenBank files found in {genomes_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(gbk_files)} GenBank files")
    logger.info("Running QC checks...")
    logger.info("=" * 60)
    
    # Run QC on each genome
    qc_results = []
    for gbk_file in gbk_files:
        logger.info(f"QC: {gbk_file.stem}")
        result = check_genome_record(gbk_file)
        qc_results.append(result)
        logger.info(f"  Status: {result['status']}")
        if result.get('observations'):
            obs = result['observations']
            logger.info(f"  CDS: {obs.get('cds_count', 'N/A')}, GC: {obs.get('gc_content', 'N/A')}%")
        if result.get('notes'):
            for note in result['notes']:
                logger.info(f"    ⚠️ {note}")
        logger.info("-" * 40)
    
    # Generate summary
    summary = generate_qc_summary(qc_results)
    
    # Save JSON results
    json_path = metadata_dir / "genome_qc_results.json"
    write_json(qc_results, json_path)
    logger.info(f"QC results saved to: {json_path}")
    
    # Save CSV summary
    csv_path = metadata_dir / "genome_qc_summary.csv"
    fieldnames = ['accession', 'status', 'length', 'n_count', 'cds_count', 'gc_content', 'assembly_status', 'iupac_ambiguity', 'notes']
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in qc_results:
            checks = r.get('checks', {})
            obs = r.get('observations', {})
            writer.writerow({
                'accession': r['accession'],
                'status': r['status'],
                'length': obs.get('genome_length', ''),
                'n_count': obs.get('n_count', ''),
                'cds_count': obs.get('cds_count', ''),
                'gc_content': obs.get('gc_content', ''),
                'assembly_status': checks.get('assembly_status', {}).get('value', ''),
                'iupac_ambiguity': obs.get('iupac_ambiguity_count', ''),
                'notes': '; '.join(r.get('notes', []))
            })
    logger.info(f"QC summary saved to: {csv_path}")
    
    # Generate HTML report
    html_path = results_dir / "qc_report.html"
    generate_html_report(qc_results, summary, html_path)
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SECTION 3.3.3: GENOME QUALITY CONTROL COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total genomes: {summary['total_genomes']}")
    logger.info(f"PASS: {summary['passed']}")
    logger.info(f"FAIL: {summary['failed']}")
    logger.info(f"Pass rate: {summary['pass_rate']}%")
    logger.info("=" * 60)
    
    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
