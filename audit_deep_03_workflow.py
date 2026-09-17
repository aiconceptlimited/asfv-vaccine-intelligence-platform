#!/usr/bin/env python3
"""
DEEP AUDIT 03: Inspect Snakemake workflow contents
"""
from pathlib import Path

print("=" * 60)
print("DEEP WORKFLOW INSPECTION")
print("=" * 60)

for smk in Path("workflow/rules").glob("*.smk"):
    print(f"\n📄 {smk}")
    with open(smk) as f:
        content = f.read()
    print(f"   Lines: {len(content.split(chr(10)))}")
    
    # Find rules
    rules = []
    for line in content.split('\n'):
        if 'rule ' in line and ':' in line:
            rules.append(line.strip())
    if rules:
        print(f"   Rules: {len(rules)}")
        for r in rules:
            print(f"     {r}")
    
    # Find inputs/outputs
    inputs = [l.strip() for l in content.split('\n') if 'input:' in l]
    outputs = [l.strip() for l in content.split('\n') if 'output:' in l]
    if inputs:
        print(f"   Inputs: {len(inputs)}")
    if outputs:
        print(f"   Outputs: {len(outputs)}")
    
    # Find shell/script
    if 'shell:' in content:
        print(f"   Uses shell: Yes")
    if 'script:' in content:
        print(f"   Uses script: Yes")

# Check Snakefile
snakefile = Path("Snakefile")
if snakefile.exists():
    print(f"\n📄 Snakefile")
    with open(snakefile) as f:
        content = f.read()
    print(f"   Lines: {len(content.split(chr(10)))}")
    rules = [l.strip() for l in content.split('\n') if 'rule ' in l and ':' in l]
    print(f"   Rules: {len(rules)}")
    for r in rules:
        print(f"     {r}")

print("\n" + "=" * 60)
