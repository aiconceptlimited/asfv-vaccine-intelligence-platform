#!/usr/bin/env python3
"""
Immutable biological constants.
"""

VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")
AMBIGUOUS_AMINO_ACIDS = set("BZJXUO")
GAP_CHARACTERS = set("-")

SUPPORTED_PROTEINS = ["p72", "p30", "p54", "CD2v", "pp220", "pCP312R"]

GENE_TO_PROTEIN = {
    "B646L": "p72",
    "CP204L": "p30",
    "E183L": "p54",
    "EP402R": "CD2v",
    "CP2475L": "pp220",
    "CP312R": "pCP312R"
}

PROTEIN_TO_GENE = {v: k for k, v in GENE_TO_PROTEIN.items()}

PROTEIN_PROCESSING_ORDER = [
    ("p72", "B646L"),
    ("p30", "CP204L"),
    ("p54", "E183L"),
    ("CD2v", "EP402R"),
    ("pp220", "CP2475L"),
    ("pCP312R", "CP312R")
]
