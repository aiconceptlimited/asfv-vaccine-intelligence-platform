#!/usr/bin/env python3
"""
Stage 1: Literature Verification
Checks if SLA frequency data is properly sourced
"""

import pandas as pd
import os

print("=" * 80)
print("STAGE 1: LITERATURE VERIFICATION")
print("=" * 80)

# Load evidence table
evidence_file = "sla_frequency_evidence.csv"
if not os.path.exists(evidence_file):
    print("❌ Evidence file not found: sla_frequency_evidence.csv")
    print("STOP: Cannot proceed without evidence file")
    sys.exit(1)

df = pd.read_csv(evidence_file)
print(f"\n✅ Evidence file loaded: {len(df)} rows")

# Check for unverified entries
unverified = df[df['verified'] == False]
if len(unverified) > 0:
    print(f"\n⚠️ Found {len(unverified)} unverified entries:")
    for idx, row in unverified.iterrows():
        print(f"  {row['allele']}: {row['notes']}")
    print("\n❌ STOP: Unverified entries found. Cannot proceed.")
    print("Please verify each entry and set verified = TRUE")
    sys.exit(1)

print("\n✅ All entries verified. Proceeding to Stage 2.")
