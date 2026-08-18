#!/usr/bin/env python3
"""
Update classification of SLA alleles in the metadata
Ensures "Other SLA loci" is correctly reflected
"""

import json
import re

# Load metadata
with open('data/processed/sla/reference_panel_final/reference_panel_metadata.json', 'r') as f:
    data = json.load(f)

# Define loci classification
class_i_loci = ['SLA-1', 'SLA-2', 'SLA-3', 'SLA-6']
class_ii_loci = ['SLA-DRB', 'SLA-DQB1', 'SLA-DQA', 'SLA-DRA', 'SLA-DMA']
other_loci_patterns = ['SLA-4', 'SLA-7', 'SLA-8', 'SLA-9', 'TAP1', 'TAP2', 'DOB1']

# Count classifications
counts = {'Class I': 0, 'Class II': 0, 'Other SLA loci': 0}

# Reclassify each allele based on locus
for allele in data['alleles']:
    locus = allele.get('locus', '')
    if any(l in locus for l in class_i_loci):
        allele['class'] = 'I'
        counts['Class I'] += 1
    elif any(l in locus for l in class_ii_loci):
        allele['class'] = 'II'
        counts['Class II'] += 1
    else:
        allele['class'] = 'Other SLA loci'
        counts['Other SLA loci'] += 1

# Update summary counts
data['class_i_count'] = counts['Class I']
data['class_ii_count'] = counts['Class II']
data['other_loci_count'] = counts['Other SLA loci']

# Save updated metadata
with open('data/processed/sla/reference_panel_final/reference_panel_metadata.json', 'w') as f:
    json.dump(data, f, indent=2)

print("=== Updated Classification ===")
print(f"  Class I: {counts['Class I']}")
print(f"  Class II: {counts['Class II']}")
print(f"  Other SLA loci: {counts['Other SLA loci']}")
