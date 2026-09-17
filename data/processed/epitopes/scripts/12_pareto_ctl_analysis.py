#!/usr/bin/env python3
"""
12_pareto_ctl_analysis.py

Proper Pareto multi-objective optimization for CTL epitope selection.
Follows proposal methodology (Section 3.11.4 - 3.11.7).

Objectives:
1. Maximize SLA-I population coverage (allele breadth)
2. Maximize conservation across ASFV isolates
3. Maximize experimental/SLA-specific evidence
4. Minimize prediction uncertainty (Maximize NetMHCpan score)
5. Minimize allergenicity concern (as soft constraint)

Hard Constraints:
- ToxinPred2: ML < 0.6 (non-toxic)
- Pig-proteome similarity: No exact matches

Date: 2026-08-25
"""

import pandas as pd
import itertools
from pathlib import Path
import json

# ============================================================================
# INPUT DATA - Four Non-Toxic Candidates
# ============================================================================

CANDIDATES = [
    {
        "id": "CTL_pp220_1362",
        "peptide": "HIDKNIIQY",
        "protein": "pp220",
        "start": 1362,
        "end": 1370,
        "allele_count": 4,
        "alleles": ["SLA-1:0101", "SLA-1:0401", "SLA-1:1201", "SLA-2:0401"],
        "conservation": 1.0,
        "evidence_tier": "Tier 1A",
        "evidence_score": 4,  # Tier 1A = 4, Tier 2 = 3, Tier 3 = 2
        "netmhcpan_score": 0.767,
        "ml_score": 0.28,
        "toxicity_flag": False,
        "allergenicity_flag": False,
        "pig_proteome_match": False
    },
    {
        "id": "CTL_pp220_2008",
        "peptide": "RSIPLANIY",
        "protein": "pp220",
        "start": 2008,
        "end": 2016,
        "allele_count": 5,
        "alleles": ["SLA-1:0401", "SLA-1:1201", "SLA-2:0401", "SLA-3:0301", "SLA-3:0401"],
        "conservation": 0.9,
        "evidence_tier": "Tier 3",
        "evidence_score": 2,  # Tier 3 = 2
        "netmhcpan_score": 0.753,
        "ml_score": 0.16,
        "toxicity_flag": False,
        "allergenicity_flag": True,
        "pig_proteome_match": False
    },
    {
        "id": "CTL_pp220_1771",
        "peptide": "SAMEVLHEL",
        "protein": "pp220",
        "start": 1771,
        "end": 1779,
        "allele_count": 5,
        "alleles": ["SLA-1:0101", "SLA-1:1201", "SLA-2:0401", "SLA-3:0301", "SLA-3:0401"],
        "conservation": 0.9,
        "evidence_tier": "Tier 2",
        "evidence_score": 3,  # Tier 2 = 3
        "netmhcpan_score": 0.753,
        "ml_score": 0.18,
        "toxicity_flag": False,
        "allergenicity_flag": True,
        "pig_proteome_match": False
    },
    {
        "id": "CTL_pp220_501",
        "peptide": "YTDIVQKKY",
        "protein": "pp220",
        "start": 501,
        "end": 509,
        "allele_count": 3,
        "alleles": ["SLA-1:0401", "SLA-1:1201", "SLA-2:0401"],
        "conservation": 1.0,
        "evidence_tier": "Tier 2",
        "evidence_score": 3,  # Tier 2 = 3
        "netmhcpan_score": 0.683,
        "ml_score": 0.34,
        "toxicity_flag": False,
        "allergenicity_flag": True,
        "pig_proteome_match": False
    }
]

# ============================================================================
# OBJECTIVE DEFINITIONS (Proposal Section 3.11.4)
# ============================================================================

def calculate_allele_breadth(panel, all_possible_alleles):
    """Maximize: SLA-I population coverage (fraction of alleles covered)"""
    covered = set()
    for c in panel:
        covered.update(c["alleles"])
    return len(covered) / len(all_possible_alleles) if all_possible_alleles else 0

def calculate_unique_alleles(panel):
    """Maximize: number of unique alleles covered"""
    covered = set()
    for c in panel:
        covered.update(c["alleles"])
    return len(covered)

def calculate_avg_conservation(panel):
    """Maximize: conservation across ASFV isolates"""
    return sum(c["conservation"] for c in panel) / len(panel)

def calculate_evidence_score(panel):
    """Maximize: experimental evidence (Tier 1A=4, Tier 2=3, Tier 3=2)"""
    return sum(c["evidence_score"] for c in panel)

def calculate_avg_netmhcpan(panel):
    """Maximize: prediction confidence (higher NetMHCpan score = better binding)"""
    return sum(c["netmhcpan_score"] for c in panel) / len(panel)

def calculate_avg_ml(panel):
    """Maximize: ML prediction score"""
    return sum(c["ml_score"] for c in panel) / len(panel)

def calculate_allergen_count(panel):
    """Minimize: number of allergen-flagged peptides"""
    return sum(1 for c in panel if c["allergenicity_flag"])

def calculate_source_protein_diversity(panel):
    """Maximize: diversity of source proteins"""
    proteins = set(c["protein"] for c in panel)
    return len(proteins)

def calculate_panel_size_score(panel):
    """Penalize larger panels (prefer 3 over 4)"""
    return 1.0 if len(panel) == 3 else 0.5 if len(panel) == 2 else 0.0

# ============================================================================
# DOMINANCE CHECK
# ============================================================================

def dominates(row1, row2, objectives):
    """
    Check if row1 dominates row2 across all objectives.
    Maximization: higher is better.
    Minimization: lower is better.
    """
    # Check if row1 is at least as good as row2 in all objectives
    at_least = True
    strictly_better = False
    
    for obj, direction in objectives.items():
        if direction == "max":
            if row1[obj] < row2[obj] - 1e-9:
                at_least = False
                break
            if row1[obj] > row2[obj] + 1e-9:
                strictly_better = True
        elif direction == "min":
            if row1[obj] > row2[obj] + 1e-9:
                at_least = False
                break
            if row1[obj] < row2[obj] - 1e-9:
                strictly_better = True
    
    return at_least and strictly_better

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 80)
    print("PARETO CTL OPTIMIZATION - PROPER ANALYSIS")
    print("Following Proposal Section 3.11.4 - 3.11.7")
    print("=" * 80)
    print()
    
    # All possible SLA alleles
    all_alleles = set()
    for c in CANDIDATES:
        all_alleles.update(c["alleles"])
    
    print(f"Total candidates: {len(CANDIDATES)}")
    print(f"Total SLA alleles: {len(all_alleles)}")
    print()
    
    # ========================================================================
    # Generate all combinations
    # ========================================================================
    
    results = []
    
    for size in [2, 3, 4]:
        for combo in itertools.combinations(CANDIDATES, size):
            panel = list(combo)
            
            # Calculate all objectives
            result = {
                "peptides": [c["peptide"] for c in panel],
                "peptide_ids": [c["id"] for c in panel],
                "panel_size": len(panel),
                "allele_breadth": calculate_allele_breadth(panel, all_alleles),
                "unique_alleles": calculate_unique_alleles(panel),
                "avg_conservation": calculate_avg_conservation(panel),
                "evidence_score": calculate_evidence_score(panel),
                "avg_netmhcpan": calculate_avg_netmhcpan(panel),
                "avg_ml": calculate_avg_ml(panel),
                "allergen_count": calculate_allergen_count(panel),
                "protein_diversity": calculate_source_protein_diversity(panel),
                "size_score": calculate_panel_size_score(panel),
                # Individual candidate data for traceability
                "candidates": [c["peptide"] for c in panel]
            }
            
            results.append(result)
    
    df = pd.DataFrame(results)
    
    # ========================================================================
    # Sort by primary objectives
    # ========================================================================
    
    print("=" * 80)
    print("ALL EVALUATED COMBINATIONS")
    print("=" * 80)
    
    # Sort for display
    df_display = df.sort_values(
        by=['allele_breadth', 'unique_alleles', 'avg_conservation', 
            'evidence_score', 'avg_ml'],
        ascending=[False, False, False, False, False]
    )
    
    print(df_display[['peptides', 'panel_size', 'allele_breadth', 'unique_alleles', 
                     'avg_conservation', 'evidence_score', 'avg_ml', 'allergen_count']].to_string(index=False))
    print()
    
    # ========================================================================
    # Focus on 3-peptide panels
    # ========================================================================
    
    df_3 = df[df['panel_size'] == 3]
    
    print("=" * 80)
    print("3-PEPTIDE PANEL COMPARISON")
    print("=" * 80)
    
    df_3_display = df_3.sort_values(
        by=['allele_breadth', 'unique_alleles', 'avg_conservation', 
            'evidence_score', 'avg_ml'],
        ascending=[False, False, False, False, False]
    )
    
    print(df_3_display[['peptides', 'allele_breadth', 'unique_alleles', 
                       'avg_conservation', 'evidence_score', 'avg_ml', 'allergen_count']].to_string(index=False))
    print()
    
    # ========================================================================
    # Pareto Dominance Analysis (3-peptide panels only)
    # ========================================================================
    
    print("=" * 80)
    print("PARETO DOMINANCE ANALYSIS (3-Peptide Panels)")
    print("=" * 80)
    
    objectives = {
        "allele_breadth": "max",
        "unique_alleles": "max",
        "avg_conservation": "max",
        "evidence_score": "max",
        "avg_netmhcpan": "max",
        "avg_ml": "max",
        "allergen_count": "min",
        "protein_diversity": "max"
    }
    
    # Find non-dominated panels
    non_dominated = []
    dominated_by = {}
    
    for i, row1 in df_3.iterrows():
        is_dominated = False
        dominators = []
        
        for j, row2 in df_3.iterrows():
            if i != j:
                if dominates(row2, row1, objectives):
                    is_dominated = True
                    dominators.append(j)
        
        if not is_dominated:
            non_dominated.append(i)
        else:
            dominated_by[i] = dominators
    
    print(f"Non-dominated 3-peptide panels: {len(non_dominated)}")
    print()
    
    # Show non-dominated panels
    df_non_dom = df_3.loc[non_dominated]
    df_non_dom_display = df_non_dom.sort_values(
        by=['allele_breadth', 'unique_alleles', 'avg_conservation', 
            'evidence_score', 'avg_ml'],
        ascending=[False, False, False, False, False]
    )
    
    print("Non-dominated panels:")
    print(df_non_dom_display[['peptides', 'allele_breadth', 'unique_alleles', 
                             'avg_conservation', 'evidence_score', 'avg_ml', 
                             'allergen_count']].to_string(index=False))
    print()
    
    # Show dominance relationships
    print("Dominance relationships:")
    for i in non_dominated:
        dominated = []
        for j in df_3.index:
            if j not in non_dominated and i != j:
                if dominates(df_3.loc[i], df_3.loc[j], objectives):
                    dominated.append(df_3.loc[j]['peptides'])
        if dominated:
            print(f"  Panel {df_3.loc[i]['peptides']} dominates:")
            for d in dominated:
                print(f"    - {d}")
    
    # ========================================================================
    # Historical Panel Analysis
    # ========================================================================
    
    print()
    print("=" * 80)
    print("HISTORICAL PANEL ANALYSIS")
    print("=" * 80)
    
    historical = ['HIDKNIIQY', 'RSIPLANIY', 'YTDIVQKKY']
    alternative = ['HIDKNIIQY', 'SAMEVLHEL', 'YTDIVQKKY']
    
    hist_row = df_3[df_3['peptides'].apply(lambda x: sorted(x) == sorted(historical))]
    alt_row = df_3[df_3['peptides'].apply(lambda x: sorted(x) == sorted(alternative))]
    
    print(f"Historical panel: {historical}")
    print(f"Alternative panel: {alternative}")
    print()
    
    if not hist_row.empty:
        print("Historical panel metrics:")
        print(hist_row[['allele_breadth', 'unique_alleles', 'avg_conservation', 
                       'evidence_score', 'avg_netmhcpan', 'avg_ml', 
                       'allergen_count', 'protein_diversity']].to_string(index=False))
    else:
        print("Historical panel NOT FOUND in evaluated panels!")
    
    print()
    
    if not alt_row.empty:
        print("Alternative panel metrics:")
        print(alt_row[['allele_breadth', 'unique_alleles', 'avg_conservation', 
                      'evidence_score', 'avg_netmhcpan', 'avg_ml', 
                      'allergen_count', 'protein_diversity']].to_string(index=False))
    else:
        print("Alternative panel NOT FOUND in evaluated panels!")
    
    print()
    
    # ========================================================================
    # Compare Historical vs Alternative
    # ========================================================================
    
    if not hist_row.empty and not alt_row.empty:
        print("Comparison:")
        
        # Check dominance
        if dominates(hist_row.iloc[0], alt_row.iloc[0], objectives):
            print("  ✅ Historical panel dominates alternative panel")
        elif dominates(alt_row.iloc[0], hist_row.iloc[0], objectives):
            print("  ✅ Alternative panel dominates historical panel")
        else:
            print("  ⚠️ Neither panel dominates the other (Pareto-equivalent)")
        
        # Show metric differences
        print()
        print("Metric differences (Historical - Alternative):")
        for col in ['allele_breadth', 'unique_alleles', 'avg_conservation', 
                    'evidence_score', 'avg_netmhcpan', 'avg_ml', 
                    'allergen_count', 'protein_diversity']:
            diff = hist_row.iloc[0][col] - alt_row.iloc[0][col]
            if abs(diff) > 1e-9:
                print(f"  {col}: {diff:+.4f}")
    
    # ========================================================================
    # Recommendation
    # ========================================================================
    
    print()
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if not hist_row.empty and not alt_row.empty:
        if dominates(alt_row.iloc[0], hist_row.iloc[0], objectives):
            print("RECOMMENDED: Switch to alternative panel")
            print(f"  Panel: {alternative}")
            print("  Rationale: Alternative panel dominates historical panel")
            print("  across all defined objectives.")
        elif dominates(hist_row.iloc[0], alt_row.iloc[0], objectives):
            print("RECOMMENDED: Keep historical panel")
            print(f"  Panel: {historical}")
            print("  Rationale: Historical panel dominates alternative panel")
            print("  across all defined objectives.")
        else:
            print("RECOMMENDATION: Either panel is Pareto-equivalent.")
            print("  Additional tie-breaking rule needed:")
            print("  - Choose based on SLA allele coverage pattern")
            print("  - Choose based on source protein diversity")
            print("  - Choose based on minimal allergenicity")
            print()
            print("  Historical panel:", historical)
            print("  Alternative panel:", alternative)
    
    # ========================================================================
    # Save results
    # ========================================================================
    
    output_file = Path("pareto_analysis_complete.csv")
    df.to_csv(output_file, index=False)
    print(f"\n✅ Complete results saved to {output_file}")
    
    # Also save non-dominated panels
    if non_dominated:
        nd_file = Path("pareto_non_dominated_panels.csv")
        df_non_dom.to_csv(nd_file, index=False)
        print(f"✅ Non-dominated panels saved to {nd_file}")

if __name__ == "__main__":
    main()
