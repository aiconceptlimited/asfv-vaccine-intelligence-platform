#!/usr/bin/env python3
"""
Canonical Epitope Record (CER) as a dataclass.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from .enums import EpitopeType


@dataclass
class CanonicalEpitopeRecord:
    """Canonical Epitope Record - standardized epitope representation."""

    # Required fields
    epitope_id: str
    protein: str
    gene: str
    epitope_type: EpitopeType
    peptide: str
    start: int
    end: int
    length: int
    prediction_tool: str
    score: float
    rank: float
    conservation: float
    prediction_date: str = field(default_factory=lambda: datetime.now().isoformat())
    source_alignment: str = "v1.0"

    # CTL-specific fields
    sla_class_I_allele: Optional[str] = None
    binding_affinity: Optional[float] = None
    percentile_rank: Optional[float] = None
    binder_class: Optional[str] = None

    # HTL-specific fields
    sla_class_II_allele: Optional[str] = None
    binding_core: Optional[str] = None

    # B-cell-specific fields
    probability: Optional[float] = None
    threshold: Optional[float] = None
    exposed_residue_fraction: Optional[float] = None

    # Consensus fields
    ctl_support: int = 0
    htl_support: int = 0
    bcell_support: int = 0
    total_support: int = 0
    predicted_by: str = ""
    consensus_status: str = "Candidate"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "epitope_id": self.epitope_id,
            "protein": self.protein,
            "gene": self.gene,
            "epitope_type": self.epitope_type.value,
            "peptide": self.peptide,
            "start": self.start,
            "end": self.end,
            "length": self.length,
            "prediction_tool": self.prediction_tool,
            "score": self.score,
            "rank": self.rank,
            "conservation": self.conservation,
            "prediction_date": self.prediction_date,
            "source_alignment": self.source_alignment,
            "sla_class_I_allele": self.sla_class_I_allele,
            "binding_affinity": self.binding_affinity,
            "percentile_rank": self.percentile_rank,
            "binder_class": self.binder_class,
            "sla_class_II_allele": self.sla_class_II_allele,
            "binding_core": self.binding_core,
            "probability": self.probability,
            "threshold": self.threshold,
            "exposed_residue_fraction": self.exposed_residue_fraction,
            "ctl_support": self.ctl_support,
            "htl_support": self.htl_support,
            "bcell_support": self.bcell_support,
            "total_support": self.total_support,
            "predicted_by": self.predicted_by,
            "consensus_status": self.consensus_status
        }

    def to_tsv_row(self) -> Dict[str, Any]:
        """Return a TSV-compatible row."""
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanonicalEpitopeRecord':
        """Create a CER from a dictionary."""
        epitope_type = data.get("epitope_type")
        if isinstance(epitope_type, str):
            epitope_type = EpitopeType(epitope_type)

        return cls(
            epitope_id=data["epitope_id"],
            protein=data["protein"],
            gene=data["gene"],
            epitope_type=epitope_type,
            peptide=data["peptide"],
            start=data["start"],
            end=data["end"],
            length=data["length"],
            prediction_tool=data["prediction_tool"],
            score=data["score"],
            rank=data["rank"],
            conservation=data["conservation"],
            prediction_date=data.get("prediction_date", datetime.now().isoformat()),
            source_alignment=data.get("source_alignment", "v1.0"),
            sla_class_I_allele=data.get("sla_class_I_allele"),
            binding_affinity=data.get("binding_affinity"),
            percentile_rank=data.get("percentile_rank"),
            binder_class=data.get("binder_class"),
            sla_class_II_allele=data.get("sla_class_II_allele"),
            binding_core=data.get("binding_core"),
            probability=data.get("probability"),
            threshold=data.get("threshold"),
            exposed_residue_fraction=data.get("exposed_residue_fraction"),
            ctl_support=data.get("ctl_support", 0),
            htl_support=data.get("htl_support", 0),
            bcell_support=data.get("bcell_support", 0),
            total_support=data.get("total_support", 0),
            predicted_by=data.get("predicted_by", ""),
            consensus_status=data.get("consensus_status", "Candidate")
        )

    def __repr__(self) -> str:
        return f"CER({self.epitope_id}: {self.peptide} [{self.epitope_type.value}])"
