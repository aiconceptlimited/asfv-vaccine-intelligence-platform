#!/usr/bin/env python3
"""
Module 1: Sequence QC
"""

import sys
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from common import (
    DEFAULT_CONFIG, QCStatus, ExitCode,
    read_fasta, read_json, write_json, write_fasta,
    generate_checksum, ensure_directory,
    setup_logging,
    SEQUENCE_QC_SCHEMA,
    validate_against_schema,
    validate_fasta, validate_sequence, validate_conservation, validate_linkage,
    PROTEIN_TO_GENE,
    ProteinFileMissingError, InvalidFastaError
)

MODULE_NAME = "01_sequence_qc"
MODULE_VERSION = "1.1.0"

EXPECTED_LENGTHS = {
    "B646L": 646, "CP204L": 194, "E183L": 183,
    "EP402R": 402, "CP2475L": 2475, "CP312R": 312
}


def compute_conservation_stats(conservation_data):
    """Compute mean conservation and highly conserved residues."""
    if not conservation_data or not isinstance(conservation_data, list):
        return 0, 0
    frequencies = [item.get('frequency', 0) for item in conservation_data if isinstance(item, dict)]
    if not frequencies:
        return 0, 0
    mean_conservation = sum(frequencies) / len(frequencies)
    highly_conserved = sum(1 for f in frequencies if f >= 99.0)
    return round(mean_conservation, 1), highly_conserved


def calculate_statistics(records: List, gene: str) -> Dict[str, Any]:
    lengths = [len(record.seq) for record in records]
    unique_seqs = len(set(str(record.seq) for record in records))
    expected_length = EXPECTED_LENGTHS.get(gene, 0)
    complete_count = 0
    partial_count = 0
    partial_sequences = []
    if expected_length:
        for record in records:
            if len(record.seq) >= expected_length:
                complete_count += 1
            else:
                partial_count += 1
                partial_sequences.append({"id": record.id, "length": len(record.seq), "expected": expected_length})
    return {
        "count": len(records),
        "minimum_length": min(lengths) if lengths else 0,
        "maximum_length": max(lengths) if lengths else 0,
        "mean_length": round(sum(lengths) / len(lengths), 2) if lengths else 0,
        "median_length": sorted(lengths)[len(lengths)//2] if lengths else 0,
        "unique_sequences": unique_seqs,
        "duplicate_sequences": len(records) - unique_seqs,
        "complete_sequences": complete_count if expected_length else len(records),
        "partial_sequences": partial_count if expected_length else 0,
        "expected_length": expected_length,
        "partial_sequence_details": partial_sequences if partial_count > 0 else []
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protein", required=True)
    parser.add_argument("--fasta", required=True)
    parser.add_argument("--conservation", required=True)
    parser.add_argument("--gene")
    parser.add_argument("--output_dir")
    parser.add_argument("--log_dir")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    gene = args.gene or PROTEIN_TO_GENE.get(args.protein, "")
    if not gene:
        print(f"Error: Could not determine gene for {args.protein}", file=sys.stderr)
        sys.exit(ExitCode.CONFIG_ERROR.value)
    
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_CONFIG.epitope_dir / args.protein
    log_dir = Path(args.log_dir) if args.log_dir else DEFAULT_CONFIG.logs_dir / "sequence_qc"
    
    logger = setup_logging(MODULE_NAME, args.protein, log_dir,
                          log_level=logging.DEBUG if args.verbose else logging.INFO)
    
    logger.info("=" * 60)
    logger.info(f"Module: {MODULE_NAME} v{MODULE_VERSION}")
    logger.info(f"Protein: {args.protein}")
    logger.info(f"Gene: {gene}")
    logger.info(f"FASTA: {args.fasta}")
    logger.info(f"Conservation: {args.conservation}")
    logger.info("=" * 60)
    
    input_dir = output_dir / "input"
    qc_dir = output_dir / "qc"
    metadata_dir = output_dir / "metadata"
    ensure_directory(input_dir)
    ensure_directory(qc_dir)
    ensure_directory(metadata_dir)
    
    qc_file = qc_dir / "sequence_qc.json"
    summary_file = metadata_dir / "protein_summary.json"
    manifest_file = metadata_dir / "manifest.json"
    
    if not args.force and qc_file.exists() and summary_file.exists() and manifest_file.exists():
        logger.info("Outputs already exist. Use --force to rerun.")
        sys.exit(ExitCode.SUCCESS.value)
    
    try:
        # Load and validate FASTA
        records = read_fasta(args.fasta)
        logger.info(f"Read {len(records)} sequences from FASTA")
        fasta_warnings, fasta_errors = validate_fasta(records)
        
        # Validate sequences
        seq_warnings, seq_errors = [], []
        for record in records:
            w, e = validate_sequence(str(record.seq))
            seq_warnings.extend(w)
            seq_errors.extend(e)
        
        # Calculate statistics
        statistics = calculate_statistics(records, gene)
        logger.info(f"Sequences: {statistics['count']}, Length range: {statistics['minimum_length']} - {statistics['maximum_length']} aa")
        if statistics.get('partial_sequences', 0) > 0:
            logger.warning(f"Partial sequences: {statistics['partial_sequences']}")
        
        # Generate checksums
        protein_checksum = generate_checksum(args.fasta)
        conservation_checksum = generate_checksum(args.conservation)
        
        # Validate conservation
        conservation_data = read_json(args.conservation)
        cons_warnings, cons_errors = validate_conservation(conservation_data, args.protein, gene)
        
        # Compute conservation stats
        mean_conservation, highly_conserved = compute_conservation_stats(conservation_data)
        logger.info(f"Mean conservation: {mean_conservation}%, Highly conserved: {highly_conserved}")
        
        # Validate linkage
        protein_data = {"protein": args.protein, "gene": gene, "alignment_length": statistics["maximum_length"], "number_of_sequences": statistics["count"]}
        linkage_warnings, linkage_errors = validate_linkage(protein_data, conservation_data)
        
        # Determine status
        all_errors = fasta_errors + seq_errors + cons_errors + linkage_errors
        all_warnings = fasta_warnings + seq_warnings + cons_warnings + linkage_warnings
        status = QCStatus.FAIL.value if all_errors else (QCStatus.PASS_WITH_WARNINGS.value if all_warnings else QCStatus.PASS.value)
        logger.info(f"QC Status: {status}")
        
        # Write QC report
        qc_result = {
            "status": status,
            "warnings": all_warnings,
            "errors": all_errors,
            "sequence_statistics": statistics,
            "checksums": {"protein": protein_checksum, "conservation": conservation_checksum},
            "conservation_linkage": {
                "protein": args.protein,
                "gene": gene,
                "alignment_length": statistics["maximum_length"],
                "number_of_sequences": statistics["count"],
                "matches": len(linkage_errors) == 0
            }
        }
        write_json(qc_file, qc_result)
        logger.info(f"QC report written: {qc_file}")
        
        # Write protein summary
        summary = {
            "gene": gene,
            "protein": args.protein,
            "reference_accession": "Multiple",
            "alignment_length": statistics["maximum_length"],
            "mean_conservation": mean_conservation,
            "number_of_sequences": statistics["count"],
            "complete_sequences": statistics.get("complete_sequences", statistics["count"]),
            "partial_sequences": statistics.get("partial_sequences", 0),
            "expected_length": statistics.get("expected_length", 0),
            "highly_conserved_residues": highly_conserved,
            "pipeline_version": DEFAULT_CONFIG.pipeline_version,
            "created": datetime.now().isoformat()
        }
        write_json(summary_file, summary)
        logger.info(f"Protein summary written: {summary_file}")
        
        # Write manifest
        manifest = {
            "protein": args.protein,
            "gene": gene,
            "input_fasta": args.fasta,
            "input_fasta_checksum": protein_checksum,
            "conservation_file": args.conservation,
            "conservation_checksum": conservation_checksum,
            "outputs": {
                "protein_fasta": str(input_dir / "protein.fasta"),
                "sequence_qc": str(qc_file),
                "protein_summary": str(summary_file)
            },
            "modules_completed": [],
            "current_module": MODULE_NAME,
            "pipeline_version": DEFAULT_CONFIG.pipeline_version,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "qc_status": status,
            "next_module": "02_ctl_discovery"
        }
        write_json(manifest_file, manifest)
        logger.info(f"Manifest written: {manifest_file}")
        
        write_fasta(input_dir / "protein.fasta", records)
        logger.info(f"Protein FASTA copied to: {input_dir / 'protein.fasta'}")
        
        logger.info(f"Sequence QC completed. Status: {status}")
        sys.exit(ExitCode.SUCCESS.value if status != QCStatus.FAIL.value else ExitCode.VALIDATION_FAILURE.value)
        
    except Exception as e:
        logger.error(f"Sequence QC failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(ExitCode.INTERNAL_EXCEPTION.value)


if __name__ == "__main__":
    main()
