#!/usr/bin/env python3

import requests
import pandas as pd
from datetime import date
from pathlib import Path
import time

BASE_URL = "https://query-api.iedb.org/tcell_search"

OUTDIR = Path(
    "/home/abubakar/asfv_vaccine_platform/"
    "data/processed/epitopes/datasets/ctl/raw"
)

OUTDIR.mkdir(parents=True, exist_ok=True)

OUTFILE = OUTDIR / "iedb_sla_tcell_raw.csv"

TODAY = date.today().isoformat()

print("=" * 80)
print("IEDB SLA/T-CELL EXTRACTION (FIXED)")
print("=" * 80)
print(f"API: {BASE_URL}")
print(f"Extraction date: {TODAY}")

# Simplified query that works
params = {
    "host_organism_name": "ilike.*Sus*scrofa*",
    "limit": 10000,
}

print("\nQuerying IEDB...")
print(f"Query: host_organism_name=ilike.*Sus*scrofa*")

try:
    response = requests.get(
        BASE_URL,
        params=params,
        timeout=120
    )
    response.raise_for_status()
except Exception as e:
    print("\nERROR communicating with IEDB:")
    print(e)
    raise SystemExit(1)

print(f"HTTP status: {response.status_code}")

data = response.json()
print(f"Records returned: {len(data)}")

if not data:
    print("\nWARNING: No records returned.")
    raise SystemExit(1)

# Convert to DataFrame
df = pd.DataFrame(data)

print("\nColumns returned:")
for col in df.columns:
    print("  ", col)

# Normalize sequence
if "linear_sequence" in df.columns:
    df["linear_sequence"] = (
        df["linear_sequence"]
        .astype(str)
        .str.upper()
        .str.replace(r"\s+", "", regex=True)
    )

# Keep only standard peptide sequences (8-11 aa)
if "linear_sequence" in df.columns:
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")

    def valid_sequence(seq):
        return (
            seq
            and seq != "NAN"
            and 8 <= len(seq) <= 11
            and set(seq).issubset(valid_aa)
        )

    before = len(df)
    df = df[df["linear_sequence"].apply(valid_sequence)].copy()
    print(f"\nSequence QC: {before} -> {len(df)}")

# Remove exact duplicate assay records
before = len(df)
df = df.drop_duplicates(
    subset=["linear_sequence", "tcell_id"],
    keep="first"
)
print(f"Duplicate assay removal: {before} -> {len(df)}")

# Add provenance metadata
df["dataset_source"] = "IEDB IQ-API"
df["extraction_date"] = TODAY
df["dataset_version"] = "CTL_IEDB_RAW_v1"

# Save
df.to_csv(OUTFILE, index=False)

print("\n" + "=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print(f"Saved: {OUTFILE}")
print(f"Records: {len(df)}")

if "mhc_allele_name" in df.columns and len(df) > 0:
    print("\nMHC alleles:")
    print(df["mhc_allele_name"].value_counts().head(20).to_string())

if "qualitative_measure" in df.columns and len(df) > 0:
    print("\nOutcomes:")
    print(df["qualitative_measure"].value_counts().to_string())

if "source_organism_name" in df.columns and len(df) > 0:
    print("\nSource organisms:")
    print(df["source_organism_name"].value_counts().head(20).to_string())
