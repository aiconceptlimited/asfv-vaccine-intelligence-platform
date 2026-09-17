#!/usr/bin/env python3
"""
DEEP AUDIT 01: Inspect actual contents of major datasets
"""
import json
import csv
import pandas as pd
from pathlib import Path

print("=" * 60)
print("DEEP DATASET INSPECTION")
print("=" * 60)

# 1. mapped_epitopes.json
ep_path = Path("data/processed/epitopes/mapped_epitopes.json")
if ep_path.exists():
    with open(ep_path) as f:
        data = json.load(f)
    print(f"\n📄 mapped_epitopes.json")
    print(f"   Type: {type(data).__name__}")
    if isinstance(data, dict):
        print(f"   Keys: {list(data.keys())}")
        total = 0
        for k, v in data.items():
            if isinstance(v, list):
                print(f"   {k}: {len(v)} epitopes")
                total += len(v)
        print(f"   TOTAL: {total} epitopes")
    elif isinstance(data, list):
        print(f"   Length: {len(data)}")
        if len(data) > 0:
            print(f"   First item: {data[0]}")

# 2. conservation_summary.csv
cons_path = Path("data/processed/conservation/conservation_summary.csv")
if cons_path.exists():
    try:
        df = pd.read_csv(cons_path)
        print(f"\n📄 conservation_summary.csv")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Head:")
        print(df.head().to_string())
    except Exception as e:
        print(f"   Error: {e}")

# 3. final_candidate_ranking.tsv
rank_path = Path("final_candidate_ranking.tsv")
if rank_path.exists():
    try:
        df = pd.read_csv(rank_path, sep='\t', nrows=20)
        print(f"\n📄 final_candidate_ranking.tsv")
        print(f"   First 20 rows (of {len(df) if hasattr(df, '__len__') else 'unknown'}):")
        print(f"   Columns: {list(df.columns)}")
        print(df.to_string())
    except Exception as e:
        print(f"   Error: {e}")

# 4. construct_orders_all.tsv (first 5 rows)
arch_path = Path("construct_orders_all.tsv")
if arch_path.exists():
    try:
        df = pd.read_csv(arch_path, sep='\t', nrows=5)
        print(f"\n📄 construct_orders_all.tsv")
        print(f"   First 5 rows:")
        print(f"   Columns: {list(df.columns)}")
        print(df.to_string())
    except Exception as e:
        print(f"   Error: {e}")

# 5. sla_alleles.fasta
sla_path = Path("sla_alleles.fasta")
if sla_path.exists():
    with open(sla_path) as f:
        lines = f.readlines()
    alleles = [l.strip() for l in lines if l.startswith('>')]
    print(f"\n📄 sla_alleles.fasta")
    print(f"   Total alleles: {len(alleles)}")
    for a in alleles[:10]:
        print(f"   {a}")

# 6. C05_H06_B241_final.fasta
cons_path = Path("C05_H06_B241_final.fasta")
if cons_path.exists():
    with open(cons_path) as f:
        lines = f.readlines()
    seq = ''.join(l.strip() for l in lines if not l.startswith('>'))
    print(f"\n📄 C05_H06_B241_final.fasta")
    print(f"   Length: {len(seq)} aa")
    print(f"   Sequence: {seq[:50]}...")

print("\n" + "=" * 60)
print("DEEP DATASET INSPECTION COMPLETE")
print("=" * 60)
