#!/usr/bin/env python3
"""
Module 2: CTL Discovery
"""

import sys
import argparse
import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from common import (
    DEFAULT_CONFIG, QCStatus, ExitCode,
    read_fasta, read_json, write_json, ensure_directory,
    setup_logging,
    CanonicalEpitopeRecord,
    PROTEIN_TO_GENE,
    update_manifest, read_manifest
)
from common.adapters import NetMHCpanAdapter, PigMatrixAdapter, AdapterResult

MODULE_NAME = "02_ctl_discovery"
MODULE_VERSION = "1.0.0"
CTL_PEPTIDE_LENGTHS = [8, 9, 10, 11]


def generate_peptides(sequence: str) -> List[Dict[str, Any]]:
    """Generate overlapping peptides (8-11 mers)."""
    peptides = []
    for length in CTL_PEPTIDE_LENGTHS:
        for i in range(len(sequence) - length + 1):
            peptides.append({
                'peptide': sequence[i:i+length],
                'start': i + 1,
                'end': i + length,
                'length': length
            })
    return peptides


def write_canonical_tsv(records: List[CanonicalEpitopeRecord], output_file: Path) -> None:
    """Write canonical records to TSV."""
    with open(output_file, 'w') as f:
        if records:
            fieldnames = list(records[0].to_dict().keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_dict())
        else:
            # Write header only
            f.write("epitope_id\tprotein\tgene\tepitope_type\tpeptide\tstart\tend\tlength\tprediction_tool\tscore\trank\tconservation\tprediction_date\tsource_alignment\tsla_class_I_allele\tbinding_affinity\tpercentile_rank\tbinder_class\tsla_class_II_allele\tbinding_core\tprobability\tthreshold\texposed_residue_fraction\tctl_support\thtl_support\tbcell_support\ttotal_support\tpredicted_by\tconsensus_status\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protein", required=True)
    parser.add_argument("--output_dir")
    parser.add_argument("--log_dir")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    
    gene = PROTEIN_TO_GENE.get(args.protein, "")
    if not gene:
        sys.exit(ExitCode.CONFIG_ERROR.value)
    
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_CONFIG.epitope_dir / args.protein
    log_dir = Path(args.log_dir) if args.log_dir else DEFAULT_CONFIG.logs_dir / "ctl_discovery"
    
    logger = setup_logging(MODULE_NAME, args.protein, log_dir,
                          log_level=logging.DEBUG if args.verbose else logging.INFO)
    
    logger.info("=" * 60)
    logger.info(f"Module: {MODULE_NAME} v{MODULE_VERSION}")
    logger.info(f"Protein: {args.protein}")
    logger.info(f"Gene: {gene}")
    logger.info("=" * 60)
    
    # Validate Module 1 outputs
    manifest_file = output_dir / "metadata" / "manifest.json"
    qc_file = output_dir / "qc" / "sequence_qc.json"
    
    if not manifest_file.exists() or not qc_file.exists():
        logger.error("Module 1 outputs not found. Run 01_sequence_qc.py first.")
        sys.exit(ExitCode.MISSING_INPUT.value)
    
    qc_data = read_json(qc_file)
    if qc_data.get('status') == QCStatus.FAIL.value:
        logger.error("Sequence QC failed. Cannot proceed.")
        sys.exit(ExitCode.VALIDATION_FAILURE.value)
    
    logger.info(f"✅ Module 1 status: {qc_data.get('status')}")
    
    # Load sequence
    protein_fasta = output_dir / "input" / "protein.fasta"
    records = read_fasta(protein_fasta)
    sequence = str(records[0].seq)
    logger.info(f"✅ Loaded sequence: {len(sequence)} aa")
    
    # Create directories
    raw_dir = output_dir / "ctl" / "raw"
    canonical_dir = output_dir / "ctl" / "canonical"
    merged_dir = output_dir / "ctl" / "merged"
    ensure_directory(raw_dir)
    ensure_directory(canonical_dir)
    ensure_directory(merged_dir)
    
    # Generate peptides
    peptides = generate_peptides(sequence)
    peptide_seqs = [p['peptide'] for p in peptides]
    logger.info(f"✅ Generated {len(peptides)} peptides (8-11 mers)")
    
    # Load SLA alleles
    sla_file = DEFAULT_CONFIG.sla_panel_dir / "reference_panel_all.fasta"
    alleles = []
    if sla_file.exists():
        from Bio import SeqIO
        for record in SeqIO.parse(sla_file, "fasta"):
            alleles.append(record.id)
        logger.info(f"✅ Loaded {len(alleles)} SLA alleles")
    else:
        logger.warning("SLA panel not found. Using default allele.")
        alleles = ["SLA-1*04:01"]
    
    # Run adapters
    all_records = []
    adapter_results = []
    
    # NetMHCpan
    logger.info("Running NetMHCpanAdapter...")
    adapter = NetMHCpanAdapter(alleles=alleles[:20])
    input_file = adapter.prepare_input(peptide_seqs, raw_dir)
    result = adapter.execute(input_file, raw_dir)
    # Add protein/gene info to records
    for record in result.records:
        record.protein = args.protein
        record.gene = gene
    all_records.extend(result.records)
    adapter_results.append(result.to_dict())
    logger.info(f"  Status: {result.status}, Records: {len(result.records)}")
    
    # PigMatrix
    logger.info("Running PigMatrixAdapter...")
    adapter = PigMatrixAdapter(alleles=alleles[:10])
    input_file = adapter.prepare_input(peptide_seqs, raw_dir)
    result = adapter.execute(input_file, raw_dir)
    for record in result.records:
        record.protein = args.protein
        record.gene = gene
    all_records.extend(result.records)
    adapter_results.append(result.to_dict())
    logger.info(f"  Status: {result.status}, Records: {len(result.records)}")
    
    # Save canonical records
    canonical_file = canonical_dir / "ctl_canonical.tsv"
    write_canonical_tsv(all_records, canonical_file)
    logger.info(f"✅ Saved {len(all_records)} canonical records to {canonical_file}")
    
    # Merge candidates (deduplicate by peptide + allele)
    seen = set()
    merged = []
    for record in all_records:
        key = f"{record.peptide}_{record.sla_class_I_allele}"
        if key not in seen:
            seen.add(key)
            merged.append(record.to_dict())
    
    merged_file = merged_dir / "ctl_candidates.tsv"
    if merged:
        with open(merged_file, 'w') as f:
            fieldnames = list(merged[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            for candidate in merged:
                writer.writerow(candidate)
        logger.info(f"✅ Merged {len(merged)} unique candidates to {merged_file}")
    else:
        # Write header only
        with open(merged_file, 'w') as f:
            f.write("epitope_id\tprotein\tgene\tepitope_type\tpeptide\tstart\tend\tlength\tprediction_tool\tscore\trank\tconservation\tprediction_date\tsource_alignment\tsla_class_I_allele\tbinding_affinity\tpercentile_rank\tbinder_class\tsla_class_II_allele\tbinding_core\tprobability\tthreshold\texposed_residue_fraction\tctl_support\thtl_support\tbcell_support\ttotal_support\tpredicted_by\tconsensus_status\n")
        logger.info(f"✅ Created empty merged file: {merged_file}")
    
    # Write metadata
    metadata = {
        "module": MODULE_NAME,
        "module_version": MODULE_VERSION,
        "protein": args.protein,
        "gene": gene,
        "peptide_lengths": CTL_PEPTIDE_LENGTHS,
        "total_peptides": len(peptides),
        "total_predictions": len(all_records),
        "total_candidates": len(merged),
        "adapter_results": adapter_results,
        "created": datetime.now().isoformat(),
        "status": "COMPLETED" if len(all_records) > 0 else "COMPLETED_NO_PREDICTIONS"
    }
    metadata_file = output_dir / "ctl" / "metadata.json"
    write_json(metadata_file, metadata)
    logger.info(f"✅ Metadata saved to {metadata_file}")
    
    # Update manifest
    manifest = read_manifest(manifest_file)
    manifest["outputs"]["ctl_raw"] = str(raw_dir)
    manifest["outputs"]["ctl_canonical"] = str(canonical_file)
    manifest["outputs"]["ctl_merged"] = str(merged_file)
    manifest["outputs"]["ctl_metadata"] = str(metadata_file)
    update_manifest(manifest_file, MODULE_NAME, manifest["outputs"], "PASS", "03_htl_discovery")
    logger.info("✅ Manifest updated")
    
    logger.info(f"✅ CTL Discovery completed. Total predictions: {len(all_records)}, Candidates: {len(merged)}")
    sys.exit(ExitCode.SUCCESS.value)


if __name__ == "__main__":
    main()
