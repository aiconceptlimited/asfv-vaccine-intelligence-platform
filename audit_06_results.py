#!/usr/bin/env python3
"""
AUDIT 06: Results Inventory
Produces: audit/06_results_inventory.tsv
"""
from pathlib import Path

results = []

for result_dir in Path("results").iterdir():
    if result_dir.is_dir():
        files = list(result_dir.rglob("*"))
        txt_files = [f for f in files if f.suffix == ".txt"]
        html_files = [f for f in files if f.suffix == ".html"]
        json_files = [f for f in files if f.suffix == ".json"]
        
        results.append({
            "directory": str(result_dir),
            "total_files": len(files),
            "txt_files": len(txt_files),
            "html_files": len(html_files),
            "json_files": len(json_files),
            "size_kb": round(sum(f.stat().st_size for f in files if f.is_file()) / 1024, 1)
        })

with open("audit/06_results_inventory.tsv", "w") as f:
    f.write("directory\ttotal_files\ttxt_files\thtml_files\tjson_files\tsize_kb\n")
    for r in results:
        f.write(f"{r['directory']}\t{r['total_files']}\t{r['txt_files']}\t{r['html_files']}\t{r['json_files']}\t{r['size_kb']}\n")

print(f"✅ Audit 06 complete: {len(results)} result directories")
