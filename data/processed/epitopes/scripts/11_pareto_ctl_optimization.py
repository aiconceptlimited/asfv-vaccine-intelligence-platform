#!/usr/bin/env python3
"""
11_pareto_ctl_optimization.py

Reconstruct the Pareto optimization for CTL epitope selection
from the 4 non-toxic candidates.
"""

import pandas as pd
import itertools
from pathlib import Path

# Input data
CANDIDATES = [
    {
        "id": "CTL_pp220_1362",
        "peptide": "HIDKNIIQY",
        "protein": "pp220",
        "allele_count": 4,
        "alleles": ["SLA-1:0101", "SLA-1:0401", "SLA-1:1201", "SLA-2:0401"],
        "conservation": 1.0,
        "experimental_evidence": "Tier A",
        "netmhcpan_score": 0.767,
        "ml_score": 0.28,
        "toxicity_flag": False,
        "allergenicity_flag": False
    },
    {
        "id": "CTL_pp220_2008",
        "peptide": "RSIPLANIY",
        "protein": "pp220",
        "allele_count": 5,
        "alleles": ["SLA-1:0401", "SLA-1:1201", "SLA-2:0401", "SLA-3:0301", "SLA-3:0401"],
        "conservation": 0.9,
        "experimental_evidence": "Tier B",
        "netmhcpan_score": 0.753,
        "ml_score": 0.16,
        "toxicity_flag": False,
        "allergenicity_flag": True
    },
    {
        "id": "CTL_pp220_1771",
        "peptide": "SAMEVLHEL",
        "protein": "pp220",
        "allele_count": 5,
        "alleles": ["SLA-1:0101", "SLA-1:1201", "SLA-2:0401", "SLA-3:0301", "SLA-3:0401"],
        "conservation": 0.9,
        "experimental_evidence": "Tier B",
        "netmhcpan_score": 0.753,
        "ml_score": 0.18,
        "toxicity_flag": False,
        "allergenicity_flag": True
    },
    {
        "id": "CTL_pp220_501",
        "peptide": "YTDIVQKKY",
        "protein": "pp220",
        "allele_count": 3,
        "alleles": ["SLA-1:0401", "SLA-1:1201", "SLA-2:0401"],
        "conservation": 1.0,
        "experimental_evidence": "Tier B",
        "netmhcpan_score": 0.683,
        "ml_score": 0.34,
        "toxicity_flag": False,
        "allergenicity_flag": True
    }
]

def evaluate_panel(panel):
    """Calculate all objective metrics for a panel."""
    # Unique alleles
    all_alleles = set()
    for c in panel:
        all_alleles.update(c["alleles"])
    
    # Allele breadth (fraction of all possible alleles covered)
    all_possible = set()
    for c in CANDIDATES:
        all_possible.update(c["alleles"])
    allele_breadth = len(all_alleles) / len(all_possible) if all_possible else 0
    
    # Average conservation
    avg_conservation = sum(c["conservation"] for c in panel) / len(panel)
    
    # Experimental score (Tier A=3, B=2, C=1)
    tier_scores = {"Tier A": 3, "Tier B": 2, "Tier C": 1}
    exp_score = sum(tier_scores.get(c["experimental_evidence"], 0) for c in panel)
    
    # Average NetMHCpan
    avg_netmhcpan = sum(c["netmhcpan_score"] for c in panel) / len(panel)
    
    # Average ML
    avg_ml = sum(c["ml_score"] for c in panel) / len(panel)
    
    return {
        "peptides": [c["peptide"] for c in panel],
        "panel_size": len(panel),
        "allele_breadth": allele_breadth,
        "unique_alleles": len(all_alleles),
        "avg_conservation": avg_conservation,
        "experimental_score": exp_score,
        "avg_netmhcpan": avg_netmhcpan,
        "avg_ml": avg_ml,
        "peptide_ids": [c["id"] for c in panel]
    }

def main():
    print("=" * 80)
    print("PARETO CTL OPTIMIZATION - RECONSTRUCTION")
    print("=" * 80)
    print()
    
    # Generate all combinations of sizes 2, 3, and 4
    results = []
    for size in [2, 3, 4]:
        for combo in itertools.combinations(CANDIDATES, size):
            result = evaluate_panel(list(combo))
            results.append(result)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Sort by objectives
    df_sorted = df.sort_values(
        by=['allele_breadth', 'unique_alleles', 'avg_conservation', 
            'experimental_score', 'avg_ml'],
        ascending=[False, False, False, False, False]
    )
    
    print("All evaluated combinations:")
    print(df_sorted.to_string(index=False))
    print()
    
    # Focus on 3-peptide panels
    df_3 = df[df['panel_size'] == 3]
    
    print("3-Peptide Panel Comparison:")
    print(df_3[['peptides', 'allele_breadth', 'unique_alleles', 
                'avg_conservation', 'experimental_score', 'avg_ml']].to_string(index=False))
    print()
    
    # Pareto analysis
    print("Pareto Analysis:")
    print("-" * 40)
    
    # Check dominance among 3-peptide panels
    for i, row1 in df_3.iterrows():
        for j, row2 in df_3.iterrows():
            if i != j:
                dominates = (
                    row1['allele_breadth'] >= row2['allele_breadth'] and
                    row1['unique_alleles'] >= row2['unique_alleles'] and
                    row1['avg_conservation'] >= row2['avg_conservation'] and
                    row1['experimental_score'] >= row2['experimental_score'] and
                    row1['avg_ml'] >= row2['avg_ml'] and
                    any([
                        row1['allele_breadth'] > row2['allele_breadth'],
                        row1['unique_alleles'] > row2['unique_alleles'],
                        row1['avg_conservation'] > row2['avg_conservation'],
                        row1['experimental_score'] > row2['experimental_score'],
                        row1['avg_ml'] > row2['avg_ml']
                    ])
                )
                if dominates:
                    print(f"Panel {row1['peptides']} dominates {row2['peptides']}")
    
    print()
    print("Historical panel:", ['HIDKNIIQY', 'RSIPLANIY', 'YTDIVQKKY'])
    print("Alternative panel:", ['HIDKNIIQY', 'SAMEVLHEL', 'YTDIVQKKY'])
    print()
    
    # Check historical panel metrics
    hist_panel = ['HIDKNIIQY', 'RSIPLANIY', 'YTDIVQKKY']
    hist_row = df_3[df_3['peptides'].apply(lambda x: sorted(x) == sorted(hist_panel))]
    if not hist_row.empty:
        print("Historical panel metrics:")
        print(hist_row[['allele_breadth', 'unique_alleles', 'avg_conservation', 
                       'experimental_score', 'avg_ml']].to_string(index=False))
    
    print()
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print("1. Review Pareto dominance relationships")
    print("2. Define tie-breaking rule for equivalent panels")
    print("3. Select final panel based on documented criteria")
    print("4. Compare with historical panel")
    
    # Save results
    output_file = Path("pareto_reconstructed_results.csv")
    df.to_csv(output_file, index=False)
    print(f"\n✅ Results saved to {output_file}")

if __name__ == "__main__":
    main()
