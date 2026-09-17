#!/usr/bin/env python3
"""
AUDIT 03: Scripts Inventory
Produces: audit/03_scripts_inventory.tsv
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

scripts = []

for py_file in Path(".").rglob("*.py"):
    if ".snakemake" in str(py_file) or "MixMHC2pred" in str(py_file):
        continue
    
    try:
        with open(py_file) as f:
            content = f.read()
    except:
        content = ""
    
    # Extract imports
    imports = []
    for line in content.split('\n'):
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line.strip())
    
    # Extract function definitions
    functions = re.findall(r'def\s+(\w+)\s*\(', content)
    
    # Check if script has main guard
    has_main = 'if __name__' in content
    
    # Count lines
    lines = len(content.split('\n'))
    
    scripts.append({
        "path": str(py_file),
        "lines": lines,
        "imports": len(imports),
        "functions": len(functions),
        "has_main": has_main,
        "size_kb": round(py_file.stat().st_size / 1024, 1)
    })

# Write TSV
with open("audit/03_scripts_inventory.tsv", "w") as f:
    f.write("path\tlines\timports\tfunctions\thas_main\tsize_kb\n")
    for s in scripts:
        f.write(f"{s['path']}\t{s['lines']}\t{s['imports']}\t{s['functions']}\t{s['has_main']}\t{s['size_kb']}\n")

# Summary
total_scripts = len(scripts)
total_lines = sum(s['lines'] for s in scripts)
avg_lines = total_lines // total_scripts if total_scripts else 0

with open("audit/03_scripts_summary.txt", "w") as f:
    f.write(f"SCRIPTS INVENTORY SUMMARY\n")
    f.write(f"==========================\n")
    f.write(f"Total scripts: {total_scripts}\n")
    f.write(f"Total lines: {total_lines}\n")
    f.write(f"Average lines per script: {avg_lines}\n")
    f.write(f"Scripts with main guard: {sum(1 for s in scripts if s['has_main'])}\n")

print(f"✅ Audit 03 complete: {total_scripts} scripts, {total_lines} lines")
