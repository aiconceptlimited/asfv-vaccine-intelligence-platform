#!/bin/bash

INPUT_FASTA="/home/abubakar/asfv_vaccine_platform/data/interim/proteins/merged/E183L_p54_all.fasta"
OUTPUT_DIR="/home/abubakar/asfv_vaccine_platform/data/processed/epitopes/p54/ctl"

mkdir -p "$OUTPUT_DIR"

# Extract the first sequence properly (handles multi-line FASTA)
awk '/^>/ {if (seq) print seq; seq=""; print; next} {seq = seq $0} END {print seq}' "$INPUT_FASTA" > p54_temp.fasta

# Get the header and sequence
HEADER=$(grep "^>" p54_temp.fasta | head -1)
SEQUENCE=$(grep -v "^>" p54_temp.fasta | tr -d '\n' | head -1)

echo "$HEADER" > "$OUTPUT_DIR/p54_reference.fasta"
echo "$SEQUENCE" >> "$OUTPUT_DIR/p54_reference.fasta"

echo "Reference saved to: $OUTPUT_DIR/p54_reference.fasta"
echo "Header: $HEADER"
echo "Sequence length: $(echo -n "$SEQUENCE" | wc -c) aa"
echo "First 30 aa: ${SEQUENCE:0:30}..."
echo "Last 30 aa: ${SEQUENCE: -30}"

# Save clean sequence
echo "$SEQUENCE" > "$OUTPUT_DIR/p54_reference_clean.txt"

# Calculate SHA-256
SHA256=$(sha256sum "$OUTPUT_DIR/p54_reference.fasta" | awk '{print $1}')
echo "SHA-256: $SHA256"

# Clean up
rm -f p54_temp.fasta
