#!/usr/bin/env python3
"""
extract_junctions.py
Extracts all junction-spanning peptides from each architecture
"""

import pandas as pd
from typing import List, Dict
import time

# Junction peptide lengths
SLA_I_LENGTHS = [8, 9, 10, 11]
SLA_II_LENGTHS = [15]

# Linkers (must match the main script)
LINKERS = {
    'ctl_ctl': 'AAY',
    'htl_htl': 'GPGPG',
    'bcell_bcell': 'GGS',
    'domain': 'EAAAK'
}

def extract_peptides_spanning_junction(left: str, linker: str, right: str, lengths: List[int]) -> List[Dict]:
    """
    Extract peptides of specified lengths that span the junction between left and right epitopes.
    The junction is defined as the boundary between left+linker and right.
    """
    sequence = left + linker + right
    junction_pos = len(left)  # Position where linker starts (boundary between left and linker)
    linker_start = junction_pos
    linker_end = junction_pos + len(linker)
    
    peptides = []
    
    for length in lengths:
        # Find all start positions that allow a peptide of this length to span the junction
        # The peptide must include at least 1 aa from the right side (past the linker)
        min_start = max(0, linker_end - length + 1)
        max_start = min(junction_pos, len(sequence) - length)
        
        for start in range(min_start, max_start + 1):
            peptide = sequence[start:start + length]
            # Verify it spans the actual epitope junction (not just the linker)
            # At least 1 aa from left epitope AND at least 1 aa from right epitope
            left_aa_in_peptide = max(0, min(junction_pos, start + length) - start)
            right_aa_in_peptide = max(0, start + length - linker_end)
            
            if left_aa_in_peptide > 0 and right_aa_in_peptide > 0:
                peptides.append({
                    'peptide': peptide,
                    'length': length,
                    'start': start,
                    'end': start + length,
                    'left_aa': left_aa_in_peptide,
                    'right_aa': right_aa_in_peptide,
                    'linker_aa': length - left_aa_in_peptide - right_aa_in_peptide
                })
    
    return peptides

def extract_all_junctions(row: pd.Series) -> List[Dict]:
    """Extract all junction peptides for a single architecture"""
    ctl_order = row['ctl_order'].split('|')
    htl_order = row['htl_order'].split('|')
    bcell_order = row['bcell_order'].split('|')
    
    all_junctions = []
    
    # 1. CTL-CTL junctions (SLA-I, 8-11mers)
    for i in range(len(ctl_order) - 1):
        peptides = extract_peptides_spanning_junction(
            ctl_order[i], LINKERS['ctl_ctl'], ctl_order[i+1], SLA_I_LENGTHS
        )
        for p in peptides:
            all_junctions.append({
                'architecture_id': row['architecture_id'],
                'junction_type': 'ctl_ctl',
                'assay_type': 'sla_i',
                'left_epitope': ctl_order[i],
                'right_epitope': ctl_order[i+1],
                'linker': LINKERS['ctl_ctl'],
                'peptide': p['peptide'],
                'length': p['length'],
                'start': p['start'],
                'end': p['end'],
                'left_aa': p['left_aa'],
                'right_aa': p['right_aa'],
                'linker_aa': p['linker_aa']
            })
    
    # 2. Domain junction: CTL3 → EAAAK → HTL1 (SLA-I + SLA-II)
    domain_peptides_sla_i = extract_peptides_spanning_junction(
        ctl_order[-1], LINKERS['domain'], htl_order[0], SLA_I_LENGTHS
    )
    domain_peptides_sla_ii = extract_peptides_spanning_junction(
        ctl_order[-1], LINKERS['domain'], htl_order[0], SLA_II_LENGTHS
    )
    
    for p in domain_peptides_sla_i:
        all_junctions.append({
            'architecture_id': row['architecture_id'],
            'junction_type': 'domain_ctl_htl',
            'assay_type': 'sla_i',
            'left_epitope': ctl_order[-1],
            'right_epitope': htl_order[0],
            'linker': LINKERS['domain'],
            'peptide': p['peptide'],
            'length': p['length'],
            'start': p['start'],
            'end': p['end'],
            'left_aa': p['left_aa'],
            'right_aa': p['right_aa'],
            'linker_aa': p['linker_aa']
        })
    
    for p in domain_peptides_sla_ii:
        all_junctions.append({
            'architecture_id': row['architecture_id'],
            'junction_type': 'domain_ctl_htl',
            'assay_type': 'sla_ii',
            'left_epitope': ctl_order[-1],
            'right_epitope': htl_order[0],
            'linker': LINKERS['domain'],
            'peptide': p['peptide'],
            'length': p['length'],
            'start': p['start'],
            'end': p['end'],
            'left_aa': p['left_aa'],
            'right_aa': p['right_aa'],
            'linker_aa': p['linker_aa']
        })
    
    # 3. HTL-HTL junctions (SLA-II, 15mers only)
    for i in range(len(htl_order) - 1):
        peptides = extract_peptides_spanning_junction(
            htl_order[i], LINKERS['htl_htl'], htl_order[i+1], SLA_II_LENGTHS
        )
        for p in peptides:
            all_junctions.append({
                'architecture_id': row['architecture_id'],
                'junction_type': 'htl_htl',
                'assay_type': 'sla_ii',
                'left_epitope': htl_order[i],
                'right_epitope': htl_order[i+1],
                'linker': LINKERS['htl_htl'],
                'peptide': p['peptide'],
                'length': p['length'],
                'start': p['start'],
                'end': p['end'],
                'left_aa': p['left_aa'],
                'right_aa': p['right_aa'],
                'linker_aa': p['linker_aa']
            })
    
    # 4. Domain junction: HTL3 → EAAAK → Bcell1 (SLA-I + SLA-II)
    domain_peptides_sla_i = extract_peptides_spanning_junction(
        htl_order[-1], LINKERS['domain'], bcell_order[0], SLA_I_LENGTHS
    )
    domain_peptides_sla_ii = extract_peptides_spanning_junction(
        htl_order[-1], LINKERS['domain'], bcell_order[0], SLA_II_LENGTHS
    )
    
    for p in domain_peptides_sla_i:
        all_junctions.append({
            'architecture_id': row['architecture_id'],
            'junction_type': 'domain_htl_bcell',
            'assay_type': 'sla_i',
            'left_epitope': htl_order[-1],
            'right_epitope': bcell_order[0],
            'linker': LINKERS['domain'],
            'peptide': p['peptide'],
            'length': p['length'],
            'start': p['start'],
            'end': p['end'],
            'left_aa': p['left_aa'],
            'right_aa': p['right_aa'],
            'linker_aa': p['linker_aa']
        })
    
    for p in domain_peptides_sla_ii:
        all_junctions.append({
            'architecture_id': row['architecture_id'],
            'junction_type': 'domain_htl_bcell',
            'assay_type': 'sla_ii',
            'left_epitope': htl_order[-1],
            'right_epitope': bcell_order[0],
            'linker': LINKERS['domain'],
            'peptide': p['peptide'],
            'length': p['length'],
            'start': p['start'],
            'end': p['end'],
            'left_aa': p['left_aa'],
            'right_aa': p['right_aa'],
            'linker_aa': p['linker_aa']
        })
    
    # 5. B-cell-Bcell junctions (integrity assessment only - store full junction)
    for i in range(len(bcell_order) - 1):
        junction_seq = bcell_order[i] + LINKERS['bcell_bcell'] + bcell_order[i+1]
        all_junctions.append({
            'architecture_id': row['architecture_id'],
            'junction_type': 'bcell_bcell',
            'assay_type': 'integrity',
            'left_epitope': bcell_order[i],
            'right_epitope': bcell_order[i+1],
            'linker': LINKERS['bcell_bcell'],
            'peptide': junction_seq,
            'length': len(junction_seq),
            'start': 0,
            'end': len(junction_seq),
            'left_aa': len(bcell_order[i]),
            'right_aa': len(bcell_order[i+1]),
            'linker_aa': len(LINKERS['bcell_bcell'])
        })
    
    return all_junctions

def process_all_junctions(df: pd.DataFrame) -> pd.DataFrame:
    """Extract junctions for all architectures"""
    all_junctions = []
    total = len(df)
    
    print(f"Processing {total:,} architectures...")
    start_time = time.time()
    
    for idx, row in df.iterrows():
        junctions = extract_all_junctions(row)
        all_junctions.extend(junctions)
        
        if (idx + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed
            print(f"  Processed {idx + 1:,}/{total:,} architectures ({rate:.0f}/s) -> {len(all_junctions):,} junctions so far")
    
    elapsed = time.time() - start_time
    print(f"✅ Completed {total:,} architectures in {elapsed:.2f} seconds")
    print(f"   Generated {len(all_junctions):,} junction peptides")
    
    return pd.DataFrame(all_junctions)

def main():
    print("=" * 60)
    print("ASFV Junction Extractor")
    print("=" * 60)
    
    # Load architectures
    print("\n📂 Loading architectures...")
    df = pd.read_csv('construct_orders_all.tsv', sep='\t')
    print(f"   Loaded {len(df):,} architectures")
    
    # Extract junctions
    print("\n🔬 Extracting junction peptides...")
    junction_df = process_all_junctions(df)
    
    # Summary
    print("\n📊 Junction summary:")
    print(junction_df['junction_type'].value_counts().to_string())
    print("\n📊 Assay type summary:")
    print(junction_df['assay_type'].value_counts().to_string())
    print("\n📊 Length distribution:")
    print(junction_df['length'].value_counts().sort_index().to_string())
    
    # Save
    print("\n💾 Saving to construct_junctions_all.tsv...")
    junction_df.to_csv('construct_junctions_all.tsv', sep='\t', index=False)
    
    # Create peptide lists for NetMHCpan/NetMHCIIpan
    sla_i_peptides = junction_df[junction_df['assay_type'] == 'sla_i']['peptide'].unique()
    sla_ii_peptides = junction_df[junction_df['assay_type'] == 'sla_ii']['peptide'].unique()
    
    with open('sla_i_peptides.fasta', 'w') as f:
        for i, peptide in enumerate(sla_i_peptides, 1):
            f.write(f">peptide_{i}\n{peptide}\n")
    
    with open('sla_ii_peptides.fasta', 'w') as f:
        for i, peptide in enumerate(sla_ii_peptides, 1):
            f.write(f">peptide_{i}\n{peptide}\n")
    
    print(f"\n📋 Unique peptides:")
    print(f"   SLA-I (8-11mers): {len(sla_i_peptides):,}")
    print(f"   SLA-II (15mers): {len(sla_ii_peptides):,}")
    
    print("\n" + "=" * 60)
    print("✅ JUNCTION EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"\nFiles generated:")
    print(f"  • construct_junctions_all.tsv ({len(junction_df):,} rows)")
    print(f"  • sla_i_peptides.fasta ({len(sla_i_peptides):,} peptides)")
    print(f"  • sla_ii_peptides.fasta ({len(sla_ii_peptides):,} peptides)")
    print(f"\nNext step: Run NetMHCpan and NetMHCIIpan screening")

if __name__ == "__main__":
    main()
