#!/usr/bin/env python3
"""
AUDIT 07: Provenance Inventory
Produces: audit/07_provenance_inventory.tsv
"""
from pathlib import Path
import re

provenance = []

# Find files with version indicators
patterns = [
    r'_fixed\.',
    r'_final\.',
    r'_corrected\.',
    r'_backup\.',
    r'_audited\.',
    r'_verified\.',
    r'_v\d+\.',
    r'\.bak$',
    r'\.backup$',
    r'_freeze_',
    r'_snapshot_',
]

for f in Path(".").rglob("*"):
    if f.is_file() and not ".snakemake" in str(f) and not ".git" in str(f):
        name = f.name
        for pattern in patterns:
            if re.search(pattern, name):
                provenance.append({
                    "path": str(f),
                    "name": name,
                    "pattern": pattern,
                    "size_kb": round(f.stat().st_size / 1024, 1)
                })
                break

with open("audit/07_provenance_inventory.tsv", "w") as f:
    f.write("path\tname\tpattern\tsize_kb\n")
    for p in provenance:
        f.write(f"{p['path']}\t{p['name']}\t{p['pattern']}\t{p['size_kb']}\n")

print(f"✅ Audit 07 complete: {len(provenance)} provenance artifacts")
