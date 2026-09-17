#!/usr/bin/env python3
"""
AUDIT 08: Anomalies, Duplicates, Orphans
Produces: audit/08_anomalies.tsv
"""
from pathlib import Path
from collections import defaultdict

anomalies = []

# Empty files
for f in Path(".").rglob("*"):
    if f.is_file() and f.stat().st_size == 0:
        if not ".snakemake" in str(f) and not "__pycache__" in str(f):
            anomalies.append({
                "type": "empty_file",
                "path": str(f),
                "size": 0
            })

# Very large files (>50MB)
for f in Path(".").rglob("*"):
    if f.is_file() and f.stat().st_size > 50 * 1024 * 1024:
        if not ".snakemake" in str(f) and not ".git" in str(f):
            anomalies.append({
                "type": "large_file",
                "path": str(f),
                "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
            })

# Duplicate filenames
filenames = defaultdict(list)
for f in Path(".").rglob("*"):
    if f.is_file() and not ".snakemake" in str(f):
        filenames[f.name].append(str(f))

for name, paths in filenames.items():
    if len(paths) > 1:
        anomalies.append({
            "type": "duplicate_filename",
            "name": name,
            "paths": paths,
            "count": len(paths)
        })

with open("audit/08_anomalies.tsv", "w") as f:
    f.write("type\tpath\tdetails\n")
    for a in anomalies[:100]:
        details = str(a.get('path', '') or a.get('paths', [''])[0])
        f.write(f"{a['type']}\t{details}\t{str(a)}\n")

print(f"✅ Audit 08 complete: {len(anomalies)} anomalies found")
