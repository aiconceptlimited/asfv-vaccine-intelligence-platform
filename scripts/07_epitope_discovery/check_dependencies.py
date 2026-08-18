#!/usr/bin/env python3
"""
Module: check_dependencies.py
Checks availability of all external tools and pipeline modules.
"""

import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from common import DEFAULT_CONFIG, QCStatus, read_json


def check_tool(tool_name: str, check_command: str = None) -> dict:
    """Check if a tool is available."""
    result = {
        "name": tool_name,
        "available": False,
        "path": None,
        "version": None,
        "error": None
    }
    
    path = shutil.which(tool_name)
    if path:
        result["available"] = True
        result["path"] = path
    
    if result["available"]:
        try:
            cmd = check_command or f"{tool_name} --version"
            proc = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
            if proc.returncode == 0:
                result["version"] = proc.stdout.strip().split('\n')[0][:100]
        except Exception as e:
            result["error"] = str(e)
    
    return result


def main():
    print("=" * 60)
    print("ASFV Vaccine Platform - Dependency Checker")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check prediction tools
    print("PREDICTION ENGINES")
    print("-" * 60)
    
    tools = [
        ("NetMHCpan", "netMHCpan -h", "CTL prediction (NetMHCpan-4.1)"),
        ("NetMHCIIpan", "netMHCIIpan -h", "HTL prediction (NetMHCIIpan-4.0)"),
        ("PigMatrix", "pigmatrix --help", "Porcine-specific SLA prediction"),
        ("BepiPred", "bepipred -h", "Linear B-cell prediction"),
        ("DeepLBCEPred", "deeplbcepred --help", "B-cell prediction (ML)"),
    ]
    
    for tool_name, check_cmd, description in tools:
        result = check_tool(tool_name, check_cmd)
        icon = "✅" if result["available"] else "❌"
        print(f"{icon} {tool_name:15} {result['available']}")
        print(f"     Description: {description}")
        if result["available"]:
            print(f"     Path: {result['path']}")
            if result["version"]:
                print(f"     Version: {result['version'][:60]}")
        else:
            print(f"     Status: NOT INSTALLED")
        print()
    
    # Check pipeline modules
    print("PIPELINE MODULES")
    print("-" * 60)
    
    modules = [
        ("01_sequence_qc", "scripts/07_epitope_discovery/01_sequence_qc.py"),
        ("02_ctl_discovery", "scripts/07_epitope_discovery/02_ctl_discovery.py"),
    ]
    
    for module_name, module_path in modules:
        exists = Path(module_path).exists()
        icon = "✅" if exists else "❌"
        print(f"{icon} {module_name:20} {'Found' if exists else 'Not Found'}")
    
    # Check Module 1 outputs
    print()
    print("MODULE 1 VALIDATION")
    print("-" * 60)
    
    p72_dir = DEFAULT_CONFIG.epitope_dir / "p72"
    qc_file = p72_dir / "qc" / "sequence_qc.json"
    
    if qc_file.exists():
        try:
            data = read_json(qc_file)
            status = data.get('status', 'UNKNOWN')
            icon = "✅" if status == "PASS" else "⚠️"
            print(f"{icon} Sequence QC: {status}")
            print(f"   Warnings: {len(data.get('warnings', []))}")
            print(f"   Errors: {len(data.get('errors', []))}")
        except Exception as e:
            print(f"❌ Could not read QC: {e}")
    else:
        print("❌ Module 1 not run for p72")
    
    # Check SLA panel
    print()
    print("SLA REFERENCE PANEL")
    print("-" * 60)
    
    sla_file = DEFAULT_CONFIG.sla_panel_dir / "reference_panel_all.fasta"
    if sla_file.exists():
        try:
            from Bio import SeqIO
            count = sum(1 for _ in SeqIO.parse(sla_file, "fasta"))
            print(f"✅ SLA panel loaded: {count} alleles")
        except:
            print("✅ SLA panel exists (could not count)")
    else:
        print("❌ SLA panel not found")
    
    # Summary - FIXED: uses check_tool result correctly
    print()
    print("=" * 60)
    print("SUMMARY")
    print("-" * 60)
    
    available_count = 0
    for tool_name, _, _ in tools:
        result = check_tool(tool_name)
        if result["available"]:
            available_count += 1
    
    total_tools = len(tools)
    
    if available_count == 0:
        print("⚠️  No prediction engines installed.")
        print("   Pipeline framework is complete. Install tools for real predictions.")
        print("   Next: Install NetMHCpan-4.1 from DTU Health Tech website.")
    elif available_count < total_tools:
        print(f"⚠️  {available_count}/{total_tools} prediction engines installed.")
        missing = [t[0] for t in tools if not check_tool(t[0])["available"]]
        print(f"   Missing: {', '.join(missing)}")
        print("   Install missing tools for full functionality.")
    else:
        print(f"✅ All {total_tools} prediction engines installed.")
        print("   Pipeline is ready for production.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
