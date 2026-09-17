#!/usr/bin/env python3
"""
AUDIT 04: Workflow & Configuration
Produces: audit/04_workflow_inventory.tsv
"""
import json
import yaml
from pathlib import Path

workflow = {
    "rules": [],
    "resources": [],
    "envs": [],
    "config": [],
    "entrypoints": []
}

# Rules
for rule_file in Path("workflow/rules").glob("*.smk"):
    workflow["rules"].append(str(rule_file))

# Resources
for res in Path("workflow/resources").glob("*"):
    workflow["resources"].append(str(res))

# Envs
for env in Path("workflow/envs").glob("*"):
    workflow["envs"].append(str(env))

# Config
for cfg in Path("config").glob("*.yaml"):
    workflow["config"].append(str(cfg))

# Entrypoints
for ep in Path(".").glob("Snakefile*"):
    workflow["entrypoints"].append(str(ep))

with open("audit/04_workflow_inventory.json", "w") as f:
    json.dump(workflow, f, indent=2)

print(f"✅ Audit 04 complete: {len(workflow['rules'])} rules, {len(workflow['config'])} configs")
