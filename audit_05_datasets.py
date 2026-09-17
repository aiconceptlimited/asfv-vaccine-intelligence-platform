#!/usr/bin/env python3
"""
AUDIT 05: Major Datasets Inventory
Produces: audit/05_datasets_inventory.tsv
"""
import json
import csv
import pandas as pd
from pathlib import Path

datasets = []

# Check mapped_epitopes.json
ep_path = Path("data/processed/epitopes/mapped_epitopes.json")
if ep_path.exists():
    with open(ep_path) as f:
        data = json.load(f)
    datasets.append({
        "name": "mapped_epitopes",
        "path": str(ep_path),
        "type": "json",
        "record_count": len(data) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0,
        "size_kb": round(ep_path.stat().st_size / 1024, 1)
    })

# Check conservation summary
cons_path = Path("data/processed/conservation/conservation_summary.csv")
if cons_path.exists():
    try:
        df = pd.read_csv(cons_path)
        datasets.append({
            "name": "conservation_summary",
            "path": str(cons_path),
            "type": "csv",
            "record_count": len(df),
            "columns": len(df.columns),
            "size_kb": round(cons_path.stat().st_size / 1024, 1)
        })
    except:
        pass

# Check candidate ranking
rank_path = Path("final_candidate_ranking.tsv")
if rank_path.exists():
    try:
        df = pd.read_csv(rank_path, sep='\t')
        datasets.append({
            "name": "final_candidate_ranking",
            "path": str(rank_path),
            "type": "tsv",
            "record_count": len(df),
            "columns": len(df.columns),
            "size_kb": round(rank_path.stat().st_size / 1024, 1)
        })
    except:
        pass

# Check architecture
arch_path = Path("construct_orders_all.tsv")
if arch_path.exists():
    try:
        with open(arch_path) as f:
            line_count = sum(1 for _ in f) - 1
        datasets.append({
            "name": "construct_orders_all",
            "path": str(arch_path),
            "type": "tsv",
            "record_count": line_count,
            "columns": "unknown",
            "size_kb": round(arch_path.stat().st_size / 1024, 1)
        })
    except:
        pass

# Write summary
with open("audit/05_datasets_inventory.tsv", "w") as f:
    f.write("name\tpath\ttype\trecord_count\tcolumns\tsize_kb\n")
    for d in datasets:
        f.write(f"{d['name']}\t{d['path']}\t{d['type']}\t{d['record_count']}\t{d.get('columns', 'N/A')}\t{d['size_kb']}\n")

print(f"✅ Audit 05 complete: {len(datasets)} datasets")
