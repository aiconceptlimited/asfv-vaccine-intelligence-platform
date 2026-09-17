#!/usr/bin/env python3
"""
DEEP AUDIT 04: Inspect QC results
"""
from pathlib import Path
import re

print("=" * 60)
print("DEEP QC INSPECTION")
print("=" * 60)

d5d6_dir = Path("results/final_construct/C05_H06_B241/D5_D6")
if d5d6_dir.exists():
    for tool_dir in d5d6_dir.iterdir():
        if tool_dir.is_dir():
            print(f"\n📄 {tool_dir.name}")
            for txt in tool_dir.glob("*.txt"):
                print(f"   File: {txt.name}")
                with open(txt) as f:
                    content = f.read()
                # Extract key metrics
                score = re.search(r'Overall Prediction.*?=\s*([\d.]+)', content)
                if score:
                    print(f"   Score: {score.group(1)}")
                threshold = re.search(r'Threshold.*?:\s*([\d.]+)', content)
                if threshold:
                    print(f"   Threshold: {threshold.group(1)}")
                classification = re.search(r'Probable\s+(\w+-\w+)', content)
                if classification:
                    print(f"   Classification: {classification.group(1)}")
                result = re.search(r'Result:\s*(.+)', content)
                if result:
                    print(f"   Result: {result.group(1)}")
                # Length
                length = re.search(r'Number of amino acids:\s*(\d+)', content)
                if length:
                    print(f"   Length: {length.group(1)}")
                # MW
                mw = re.search(r'Molecular weight:\s*([\d.]+)', content)
                if mw:
                    print(f"   MW: {mw.group(1)}")
                # pI
                pi = re.search(r'Theoretical pI:\s*([\d.]+)', content)
                if pi:
                    print(f"   pI: {pi.group(1)}")
                # Status
                if "NON-ANTIGEN" in content:
                    print(f"   Status: NON-ANTIGEN")
                elif "NON-ALLERGEN" in content:
                    print(f"   Status: NON-ALLERGEN")
                elif "NON-TOXIN" in content:
                    print(f"   Status: NON-TOXIN")
                elif "STABLE" in content:
                    print(f"   Status: STABLE")
                elif "FAIL" in content.upper() or "0.4766" in content:
                    print(f"   Status: ⚠️ FAIL (below threshold)")

print("\n" + "=" * 60)
print("DEEP QC INSPECTION COMPLETE")
print("=" * 60)
