#!/usr/bin/env python3
"""
AUDIT 01: Environment & Resource State
Produces: audit/01_environment.json
"""
import os
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path

output = {
    "timestamp": datetime.now().isoformat(),
    "hostname": platform.node(),
    "system": {},
    "software": {},
    "conda_envs": [],
    "resources": {}
}

# System
output["system"]["os"] = platform.platform()
output["system"]["kernel"] = platform.release()
output["system"]["architecture"] = platform.machine()

# Resources
try:
    output["resources"]["cpu_cores"] = os.cpu_count()
except:
    output["resources"]["cpu_cores"] = "unknown"

try:
    with open("/proc/meminfo") as f:
        for line in f:
            if "MemTotal" in line:
                output["resources"]["total_ram"] = line.strip()
                break
except:
    output["resources"]["total_ram"] = "unknown"

try:
    import shutil
    total, used, free = shutil.disk_usage("/")
    output["resources"]["disk_total_gb"] = round(total / (1024**3), 1)
    output["resources"]["disk_used_gb"] = round(used / (1024**3), 1)
    output["resources"]["disk_free_gb"] = round(free / (1024**3), 1)
except:
    pass

# Software versions
def get_version(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip().split('\n')[0] or result.stderr.strip().split('\n')[0]
    except:
        return "not found"

output["software"]["python"] = get_version("python3 --version")
output["software"]["conda"] = get_version("conda --version")
output["software"]["docker"] = get_version("docker --version")
output["software"]["git"] = get_version("git --version")
output["software"]["snakemake"] = get_version("snakemake --version")

# Conda environments
try:
    result = subprocess.run("conda env list", shell=True, capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if line.strip() and not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 1:
                output["conda_envs"].append(parts[0] if len(parts) >= 2 else parts[0])
except:
    pass

# Save
Path("audit").mkdir(exist_ok=True)
with open("audit/01_environment.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Audit 01 complete: {len(output['conda_envs'])} conda envs, {len(output['software'])} tools")
