#!/usr/bin/env python3
"""
JSON schemas for validating Section 3.7 outputs.
"""

SEQUENCE_QC_SCHEMA = {
    "type": "object",
    "required": ["status", "warnings", "errors", "sequence_statistics", "checksums", "conservation_linkage"],
    "properties": {
        "status": {"type": "string", "enum": ["PASS", "PASS_WITH_WARNINGS", "FAIL"]},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "errors": {"type": "array", "items": {"type": "string"}},
        "sequence_statistics": {
            "type": "object",
            "required": ["count", "minimum_length", "maximum_length", "mean_length", "median_length",
                        "unique_sequences", "duplicate_sequences"],
            "properties": {
                "count": {"type": "integer"},
                "minimum_length": {"type": "integer"},
                "maximum_length": {"type": "integer"},
                "mean_length": {"type": "number"},
                "median_length": {"type": "number"},
                "unique_sequences": {"type": "integer"},
                "duplicate_sequences": {"type": "integer"}
            }
        },
        "checksums": {
            "type": "object",
            "required": ["protein", "conservation"],
            "properties": {
                "protein": {"type": "string"},
                "conservation": {"type": "string"}
            }
        },
        "conservation_linkage": {
            "type": "object",
            "required": ["protein", "gene", "alignment_length", "number_of_sequences", "matches"],
            "properties": {
                "protein": {"type": "string"},
                "gene": {"type": "string"},
                "alignment_length": {"type": "integer"},
                "number_of_sequences": {"type": "integer"},
                "matches": {"type": "boolean"}
            }
        }
    }
}

PROTEIN_SUMMARY_SCHEMA = {
    "type": "object",
    "required": ["gene", "protein", "reference_accession", "alignment_length", "mean_conservation",
                 "number_of_sequences", "highly_conserved_residues", "pipeline_version", "created"],
    "properties": {
        "gene": {"type": "string"},
        "protein": {"type": "string"},
        "reference_accession": {"type": "string"},
        "alignment_length": {"type": "integer"},
        "mean_conservation": {"type": "number"},
        "number_of_sequences": {"type": "integer"},
        "highly_conserved_residues": {"type": "integer"},
        "pipeline_version": {"type": "string"},
        "created": {"type": "string"}
    }
}

MANIFEST_SCHEMA = {
    "type": "object",
    "required": ["protein", "gene", "input_fasta", "input_fasta_checksum", "conservation_file",
                 "conservation_checksum", "outputs", "modules_completed", "current_module",
                 "pipeline_version", "created_at", "last_updated", "qc_status"],
    "properties": {
        "protein": {"type": "string"},
        "gene": {"type": "string"},
        "input_fasta": {"type": "string"},
        "input_fasta_checksum": {"type": "string"},
        "conservation_file": {"type": "string"},
        "conservation_checksum": {"type": "string"},
        "outputs": {"type": "object"},
        "modules_completed": {"type": "array", "items": {"type": "string"}},
        "current_module": {"type": "string"},
        "pipeline_version": {"type": "string"},
        "created_at": {"type": "string"},
        "last_updated": {"type": "string"},
        "qc_status": {"type": "string"},
        "next_module": {"type": "string"}
    }
}

PROVENANCE_SCHEMA = {
    "type": "object",
    "required": ["pipeline_version", "module", "protein", "gene", "software", "checksums",
                 "environment", "execution_timestamp", "status"],
    "properties": {
        "pipeline_version": {"type": "string"},
        "module": {"type": "string"},
        "protein": {"type": "string"},
        "gene": {"type": "string"},
        "software": {"type": "object"},
        "checksums": {"type": "object"},
        "environment": {"type": "object"},
        "execution_timestamp": {"type": "string"},
        "status": {"type": "string"},
        "execution_duration_seconds": {"type": "number"}
    }
}

PREDICTION_QC_SCHEMA = {
    "type": "object",
    "required": ["status", "warnings", "errors", "checks_passed", "checks_failed", "total_checks"],
    "properties": {
        "status": {"type": "string", "enum": ["PASS", "PASS_WITH_WARNINGS", "FAIL"]},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "errors": {"type": "array", "items": {"type": "string"}},
        "checks_passed": {"type": "integer"},
        "checks_failed": {"type": "integer"},
        "total_checks": {"type": "integer"}
    }
}

# ============================================
# Validation functions
# ============================================

def validate_against_schema(data, schema):
    """
    Validate data against a JSON schema.
    
    This is a simple validation function that checks required fields.
    For full JSON schema validation, install jsonschema.
    """
    # Check required fields
    if 'required' in schema:
        for field in schema['required']:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
    
    # Check field types
    if 'properties' in schema:
        for field, rules in schema['properties'].items():
            if field in data:
                field_type = rules.get('type')
                if field_type == 'string' and not isinstance(data[field], str):
                    raise ValueError(f"Field {field} should be string, got {type(data[field])}")
                elif field_type == 'integer' and not isinstance(data[field], int):
                    raise ValueError(f"Field {field} should be integer, got {type(data[field])}")
                elif field_type == 'number' and not isinstance(data[field], (int, float)):
                    raise ValueError(f"Field {field} should be number, got {type(data[field])}")
                elif field_type == 'object' and not isinstance(data[field], dict):
                    raise ValueError(f"Field {field} should be object, got {type(data[field])}")
                elif field_type == 'array' and not isinstance(data[field], list):
                    raise ValueError(f"Field {field} should be array, got {type(data[field])}")
                elif field_type == 'boolean' and not isinstance(data[field], bool):
                    raise ValueError(f"Field {field} should be boolean, got {type(data[field])}")
    
    # Check enum values
    if 'properties' in schema:
        for field, rules in schema['properties'].items():
            if field in data and 'enum' in rules:
                if data[field] not in rules['enum']:
                    raise ValueError(f"Field {field} has invalid value: {data[field]}")
    
    return True


def validate_json_file(file_path, schema):
    """
    Validate a JSON file against a schema.
    
    Args:
        file_path: Path to JSON file
        schema: JSON schema to validate against
    
    Returns:
        bool: True if valid, False otherwise
    """
    import json
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        validate_against_schema(data, schema)
        return True
    except Exception as e:
        print(f"Validation error in {file_path}: {e}")
        return False
