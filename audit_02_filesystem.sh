#!/bin/bash
# AUDIT 02: Complete Filesystem Inventory
# Produces: audit/02_filesystem_inventory.tsv

mkdir -p audit

echo "=== FILESYSTEM INVENTORY ==="
echo "Generating file inventory..."

# Full file inventory with metadata
find . -type f ! -path "./.snakemake/*" ! -path "./.git/*" ! -path "./temp/*" ! -path "./MixMHC2pred/.git/*" -printf "%p\t%TY-%Tm-%Td %TH:%TM:%TS\t%s\t%u\t%g\n" 2>/dev/null | \
    sed 's|^\./||' | \
    sort > audit/02_filesystem_inventory_raw.tsv

# Directory inventory
find . -type d ! -path "./.snakemake/*" ! -path "./.git/*" ! -path "./temp/*" ! -path "./MixMHC2pred/.git/*" 2>/dev/null | \
    sed 's|^\./||' | \
    sort > audit/02_directories_inventory.txt

# Summary
total_files=$(wc -l < audit/02_filesystem_inventory_raw.tsv)
total_dirs=$(wc -l < audit/02_directories_inventory.txt)

echo "total_files: $total_files"
echo "total_directories: $total_dirs"

cat > audit/02_filesystem_summary.txt << EOF
FILESYSTEM INVENTORY SUMMARY
============================
Total files: $total_files
Total directories: $total_dirs
Date: $(date)
