#!/usr/bin/env python3
"""
DEEP AUDIT 05: Inspect architecture and candidate data
"""
import pandas as pd
from pathlib import Path

print("=" * 60)
print("DEEP ARCHITECTURE INSPECTION")
print("=" * 60)

# Architecture count
arch_path = Path("construct_orders_all.tsv")
if arch_path.exists():
    try:
        with open(arch_path) as f:
            count = sum(1 for _ in f) - 1
        print(f"\n📄 construct_orders_all.tsv")
        print(f"   Total architectures: {count}")
    except:
        print(f"   Error reading file")

# Architecture enum summary
enum_path = Path("construct_enumeration_summary.json")
if enum_path.exists():
    import json
    with open(enum_path) as f:
        data = json.load(f)
    print(f"\n📄 construct_enumeration_summary.json")
    for k, v in data.items():
        print(f"   {k}: {v}")

# Candidate ranking
rank_path = Path("final_candidate_ranking.tsv")
if rank_path.exists():
    try:
        df = pd.read_csv(rank_path, sep='\t', nrows=20)
        print(f"\n📄 final_candidate_ranking.tsv")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   Top candidates:")
        # Try to find candidate names
        for col in df.columns:
            if 'candidate' in col.lower() or 'id' in col.lower() or 'name' in col.lower():
                print(f"   {col}: {df[col].iloc[:5].tolist()}")
    except Exception as e:
        print(f"   Error: {e}")

# Architecture ranking
arch_rank_path = Path("architecture_ranking_table.tsv")
if arch_rank_path.exists():
    try:
        df = pd.read_csv(arch_rank_path, sep='\t', nrows=5)
        print(f"\n📄 architecture_ranking_table.tsv")
        print(f"   Columns: {list(df.columns)}")
    except:
        pass

print("\n" + "=" * 60)
