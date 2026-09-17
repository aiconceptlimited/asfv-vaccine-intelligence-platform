#!/usr/bin/env python3
"""
DEEP AUDIT 06: Inspect CD2v and SLA data
"""
import json
from pathlib import Path

print("=" * 60)
print("DEEP CD2v & SLA INSPECTION")
print("=" * 60)

# CD2v categories
cd2v_path = Path("data/metadata/cd2v_categories.json")
if cd2v_path.exists():
    with open(cd2v_path) as f:
        data = json.load(f)
    print(f"\n📄 cd2v_categories.json")
    for category, entries in data.items():
        print(f"   {category}: {len(entries)} entries")
        for entry in entries[:3]:
            print(f"     {entry}")

# SLA alleles
sla_path = Path("sla_alleles.fasta")
if sla_path.exists():
    with open(sla_path) as f:
        lines = f.readlines()
    alleles = [l.strip().replace('>', '').split()[0] for l in lines if l.startswith('>')]
    print(f"\n📄 sla_alleles.fasta")
    print(f"   Total alleles: {len(alleles)}")
    print(f"   SLA-I: {len([a for a in alleles if 'SLA-1' in a or 'SLA-2' in a or 'SLA-3' in a])}")
    print(f"   SLA-II: {len([a for a in alleles if 'DRB' in a or 'DQA' in a or 'DQB' in a])}")
    print(f"   All alleles:")
    for a in alleles:
        print(f"     {a}")

# SLA-II methodology
method_path = Path("SLA_II_METHODOLOGY_VERIFICATION.md")
if method_path.exists():
    with open(method_path) as f:
        content = f.read()
    print(f"\n📄 SLA_II_METHODOLOGY_VERIFICATION.md")
    print(f"   Lines: {len(content.split(chr(10)))}")
    # Extract key sections
    if "NP_001107167" in content:
        print("   ✅ Contains original sequence reference")
    if "IPD SLA06007" in content:
        print("   ✅ Contains corrected sequence reference")
    if "MixMHC2pred" in content:
        print("   ✅ Contains MixMHC2pred reference")
    if "-99" in content:
        print("   ✅ Contains -99 rank issue documentation")

print("\n" + "=" * 60)
