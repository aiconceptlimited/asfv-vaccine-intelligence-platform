#!/usr/bin/env python3
"""
Kenyan SLA Population Coverage Pipeline
Provenance-controlled, stops on uncertainty
"""

import sys
import os
import subprocess
from datetime import datetime

print("=" * 80)
print("KENYAN SLA POPULATION COVERAGE PIPELINE")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("")

# Pipeline stages
stages = [
    "01_verify_literature.py",
    "02_verify_sla_alleles.py",
    "03_retrieve_sla_sequences.py",
    "04_validate_sequences.py",
    "05_prepare_netmhcpan.py",
    "06_run_netmhcpan.py",
    "07_parse_netmhcpan.py",
    "08_build_binding_matrix.py",
    "09_calculate_population_coverage.py",
    "10_compare_ctl_panels.py",
    "11_generate_qc_report.py",
    "12_generate_provenance_manifest.py",
]

for stage in stages:
    script_path = f"scripts/kenyan_sla_pipeline/{stage}"
    if os.path.exists(script_path):
        print(f"Running: {stage}")
        result = subprocess.run(["python3", script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("ERROR:", result.stderr)
        if "STOP" in result.stdout:
            print(f"Pipeline stopped at {stage}")
            sys.exit(1)
    else:
        print(f"⚠️ Script not found: {stage}")

print("")
print("=" * 80)
print("PIPELINE COMPLETE")
print("=" * 80)
