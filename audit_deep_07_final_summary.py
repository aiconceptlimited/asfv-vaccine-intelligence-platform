#!/usr/bin/env python3
"""
DEEP AUDIT 07: Final Comprehensive Summary
"""
import json
from pathlib import Path

print("=" * 70)
print("FINAL DEEP FORENSIC AUDIT SUMMARY")
print("=" * 70)

print("\n📊 PROJECT OVERVIEW")
print("-" * 40)

# Count everything
total_files = sum(1 for _ in Path(".").rglob("*") if _.is_file() and ".snakemake" not in str(_))
total_dirs = sum(1 for _ in Path(".").rglob("*") if _.is_dir() and ".snakemake" not in str(_))
total_py = len(list(Path(".").rglob("*.py")))
total_tsv = len(list(Path(".").rglob("*.tsv")))
total_csv = len(list(Path(".").rglob("*.csv")))
total_json = len(list(Path(".").rglob("*.json")))
total_fasta = len(list(Path(".").rglob("*.fasta")))

print(f"   Total Files: {total_files}")
print(f"   Total Directories: {total_dirs}")
print(f"   Python Scripts: {total_py}")
print(f"   TSV Files: {total_tsv}")
print(f"   CSV Files: {total_csv}")
print(f"   JSON Files: {total_json}")
print(f"   FASTA Files: {total_fasta}")

print("\n🔬 SCIENTIFIC DATA SUMMARY")
print("-" * 40)

# Genomes
manifest = Path("workflow/resources/accession_manifest.txt")
if manifest.exists():
    with open(manifest) as f:
        genomes = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    print(f"   Genomes: {len(genomes)}")

# Proteins
proteins = Path("data/processed/proteins/ASFV_proteins.fasta")
if proteins.exists():
    with open(proteins) as f:
        count = sum(1 for l in f if l.startswith('>'))
    print(f"   Protein Sequences: {count}")

# Epitopes
ep = Path("data/processed/epitopes/mapped_epitopes.json")
if ep.exists():
    with open(ep) as f:
        data = json.load(f)
    if isinstance(data, dict):
        total = sum(len(v) for v in data.values() if isinstance(v, list))
        print(f"   Mapped Epitopes: {total}")
    elif isinstance(data, list):
        print(f"   Mapped Epitopes: {len(data)}")

# SLA
sla = Path("sla_alleles.fasta")
if sla.exists():
    with open(sla) as f:
        alleles = [l.strip() for l in f if l.startswith('>')]
    print(f"   SLA Alleles: {len(alleles)}")

# Architecture
arch = Path("construct_orders_all.tsv")
if arch.exists():
    with open(arch) as f:
        count = sum(1 for _ in f) - 1
    print(f"   Architectures: {count:,}")

print("\n✅ AUDIT COMPLETE")
print("=" * 70)
