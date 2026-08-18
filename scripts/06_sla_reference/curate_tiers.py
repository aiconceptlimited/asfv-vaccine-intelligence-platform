#!/usr/bin/env python3
"""
Section 3.6: Tier Curation Workflow
Updates tier assignments based on literature evidence
"""

import json
import csv
from pathlib import Path

def load_current_tiers():
    """Load current tier assignments"""
    with open('data/reference/sla_tiers/sla_tier_assignments_full.json', 'r') as f:
        return json.load(f)

def save_updated_tiers(data):
    """Save updated tier assignments"""
    with open('data/reference/sla_tiers/sla_tier_assignments_curated.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("✅ Curated tier assignments saved")

def main():
    print("=" * 60)
    print("SLA Tier Curation Workflow")
    print("=" * 60)
    
    # Load current assignments
    data = load_current_tiers()
    assignments = data['assignments']
    print(f"Loaded {len(assignments)} assignments")
    
    # Example curation workflow
    print("\n📋 Curation Process:")
    print("  1. Search literature for each allele")
    print("  2. If evidence found, update tier field:")
    print("     - Tier 1: Experimental validation")
    print("     - Tier 2: African/East African evidence")
    print("  3. Add citation and rationale")
    
    print("\n📊 Current Tier Distribution:")
    tier_counts = {}
    for a in assignments:
        tier = a['tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count}")
    
    print("\n📝 Example of curated entry:")
    example = {
        "allele": "SLA-1*04:01",
        "tier": "Tier 1",
        "rationale": "Experimentally validated peptide binding",
        "evidence_type": "Published binding assay",
        "citation": "PMID: 12345678",
        "status": "CURATED"
    }
    print(json.dumps(example, indent=2))
    
    print("\n⏳  Next Steps:")
    print("  1. Curate literature evidence for each allele")
    print("  2. Update tier field in JSON")
    print("  3. Re-run pipeline with curated tiers")
    print("  4. Document changes")
    
    # Save a template for curation
    template = data.copy()
    template['curation_notes'] = {
        "date_started": "2026-08-04",
        "status": "PENDING",
        "curator": "Abubakar",
        "sources": [
            "IPD-MHC",
            "PubMed",
            "Published binding studies"
        ]
    }
    with open('data/reference/sla_tiers/sla_tier_assignments_curation_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    print("\n✅ Curation template created")

if __name__ == "__main__":
    main()
