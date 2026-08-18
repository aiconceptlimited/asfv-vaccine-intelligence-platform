#!/usr/bin/env python3
"""
Reusable validation routines.
"""

from typing import List, Tuple, Dict, Any
from Bio.SeqRecord import SeqRecord
from .constants import VALID_AMINO_ACIDS, AMBIGUOUS_AMINO_ACIDS


def validate_fasta(records: List[SeqRecord]) -> Tuple[List[str], List[str]]:
    """Validate FASTA records. Returns (warnings, errors)."""
    warnings = []
    errors = []

    if not records:
        errors.append("No records found in FASTA file")
        return warnings, errors

    seen_ids = set()
    for record in records:
        if record.id in seen_ids:
            errors.append(f"Duplicate sequence ID: {record.id}")
        seen_ids.add(record.id)

    for record in records:
        if len(record.seq) == 0:
            errors.append(f"Empty sequence: {record.id}")

    return warnings, errors


def validate_sequence(sequence: str) -> Tuple[List[str], List[str]]:
    """Validate a protein sequence. Returns (warnings, errors)."""
    warnings = []
    errors = []

    if '*' in sequence:
        errors.append("Stop codon found in sequence")

    seq_set = set(sequence.replace('-', ''))
    invalid = seq_set - VALID_AMINO_ACIDS - AMBIGUOUS_AMINO_ACIDS
    if invalid:
        errors.append(f"Invalid amino acids: {invalid}")

    ambiguous = seq_set & AMBIGUOUS_AMINO_ACIDS
    if ambiguous:
        warnings.append(f"Ambiguous residues found: {ambiguous}")

    if '-' in sequence:
        warnings.append("Gap characters found in sequence")

    return warnings, errors


def validate_peptide(peptide: str) -> Tuple[List[str], List[str]]:
    """Validate a peptide sequence. Returns (warnings, errors)."""
    warnings = []
    errors = []

    seq_set = set(peptide)
    invalid = seq_set - VALID_AMINO_ACIDS - AMBIGUOUS_AMINO_ACIDS
    if invalid:
        errors.append(f"Invalid amino acids in peptide: {invalid}")

    ambiguous = seq_set & AMBIGUOUS_AMINO_ACIDS
    if ambiguous:
        warnings.append(f"Ambiguous residues in peptide: {ambiguous}")

    if '-' in peptide:
        warnings.append("Gap characters found in peptide")

    return warnings, errors


def validate_conservation(data: Any, protein: str, gene: str) -> Tuple[List[str], List[str]]:
    """
    Validate conservation data.
    
    Handles both:
    - List of position dictionaries (position-level conservation)
    - Dictionary with metadata fields (summary conservation)
    
    Position-level list is the expected format and should PASS.
    """
    warnings = []
    errors = []

    # If data is a list (position-level conservation) - this is the expected format
    if isinstance(data, list):
        if not data:
            errors.append("Conservation list is empty")
        else:
            first_item = data[0]
            if isinstance(first_item, dict):
                # Check for expected position fields
                if 'position' in first_item and 'frequency' in first_item:
                    # This is the expected position-level format - PASS
                    pass
                else:
                    warnings.append(f"Unexpected list item fields: {list(first_item.keys())}")
            else:
                errors.append(f"Unexpected list item type: {type(first_item)}")
        return warnings, errors

    # If data is a dict (summary/conservation metadata)
    if isinstance(data, dict):
        required_fields = ['protein', 'gene', 'alignment_length', 'num_sequences']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field in conservation data: {field}")

        if 'protein' in data and data['protein'] != protein:
            errors.append(f"Protein mismatch: expected {protein}, got {data['protein']}")

        if 'gene' in data and data['gene'] != gene:
            errors.append(f"Gene mismatch: expected {gene}, got {data['gene']}")
        
        return warnings, errors

    # Unknown type
    errors.append(f"Unexpected conservation data type: {type(data)}")
    return warnings, errors


def validate_linkage(protein_data: Dict[str, Any], conservation_data: Any) -> Tuple[List[str], List[str]]:
    """
    Validate linkage between protein and conservation data.
    
    For position-level list, validates:
    - Number of positions equals alignment length
    - First position is 1
    - Last position equals alignment length
    """
    warnings = []
    errors = []

    # If conservation_data is a list (position-level)
    if isinstance(conservation_data, list):
        if not conservation_data:
            errors.append("Conservation list is empty")
            return warnings, errors
        
        alignment_length = protein_data.get('alignment_length', 0)
        
        # Validate position count
        if alignment_length and len(conservation_data) != alignment_length:
            errors.append(f"Position count mismatch: {len(conservation_data)} positions vs {alignment_length} expected")
        
        # Validate first and last positions
        first_pos = conservation_data[0].get('position', 0)
        last_pos = conservation_data[-1].get('position', 0)
        
        if first_pos != 1:
            errors.append(f"First position is {first_pos}, expected 1")
        
        if alignment_length and last_pos != alignment_length:
            errors.append(f"Last position is {last_pos}, expected {alignment_length}")
        
        # Check each position has required fields
        for item in conservation_data:
            if not isinstance(item, dict):
                errors.append(f"Non-dict item in conservation list: {type(item)}")
                break
            if 'position' not in item or 'frequency' not in item:
                errors.append(f"Missing position or frequency in item: {item}")
                break
        
        return warnings, errors

    # If conservation_data is a dict (summary data)
    if isinstance(conservation_data, dict):
        protein = protein_data.get('protein', '')
        cons_protein = conservation_data.get('protein', '')
        if protein and cons_protein and protein != cons_protein:
            errors.append(f"Protein mismatch: {protein} vs {cons_protein}")

        gene = protein_data.get('gene', '')
        cons_gene = conservation_data.get('gene', '')
        if gene and cons_gene and gene != cons_gene:
            errors.append(f"Gene mismatch: {gene} vs {cons_gene}")

        prot_length = protein_data.get('alignment_length', 0)
        cons_length = conservation_data.get('alignment_length', 0)
        if prot_length and cons_length and prot_length != cons_length:
            errors.append(f"Alignment length mismatch: {prot_length} vs {cons_length}")

        prot_seqs = protein_data.get('number_of_sequences', 0)
        cons_seqs = conservation_data.get('num_sequences', 0)
        if prot_seqs and cons_seqs and prot_seqs != cons_seqs:
            warnings.append(f"Sequence count mismatch: {prot_seqs} vs {cons_seqs}")

    return warnings, errors


def validate_coordinates(start: int, end: int, seq_length: int) -> Tuple[List[str], List[str]]:
    """Validate peptide coordinates. Returns (warnings, errors)."""
    warnings = []
    errors = []

    if start < 1:
        errors.append(f"Start position < 1: {start}")
    if end > seq_length:
        errors.append(f"End position > sequence length: {end} > {seq_length}")
    if start > end:
        errors.append(f"Start > End: {start} > {end}")

    return warnings, errors


def validate_canonical_record(record: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate a Canonical Epitope Record."""
    warnings = []
    errors = []

    required_fields = [
        "epitope_id", "protein", "gene", "epitope_type",
        "peptide", "start", "end", "length",
        "prediction_tool", "score", "rank",
        "conservation", "prediction_date", "source_alignment"
    ]

    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    epitope_type = record.get("epitope_type")
    if epitope_type == "CTL":
        optional = ["sla_class_I_allele", "binding_affinity", "percentile_rank", "binder_class"]
        for f in optional:
            if f not in record:
                warnings.append(f"Optional CTL field missing: {f}")
    elif epitope_type == "HTL":
        optional = ["sla_class_II_allele", "binding_core", "percentile_rank", "binder_class"]
        for f in optional:
            if f not in record:
                warnings.append(f"Optional HTL field missing: {f}")
    elif epitope_type == "B-cell":
        optional = ["probability", "threshold", "exposed_residue_fraction"]
        for f in optional:
            if f not in record:
                warnings.append(f"Optional B-cell field missing: {f}")

    return warnings, errors
