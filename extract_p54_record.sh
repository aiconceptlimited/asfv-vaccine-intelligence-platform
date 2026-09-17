#!/bin/bash

INPUT_FASTA="/home/abubakar/asfv_vaccine_platform/data/interim/proteins/merged/E183L_p54_all.fasta"
OUTPUT_DIR="/home/abubakar/asfv_vaccine_platform/data/processed/epitopes/p54/ctl"

mkdir -p "$OUTPUT_DIR"

# Extract ONLY the MW856067_E183L record
awk '/^>MW856067_E183L/{flag=1; print; next} /^>/{flag=0} flag' "$INPUT_FASTA" > p54_mw856067.fasta

# Count lines in extracted file
echo "Lines in extracted file: $(wc -l < p54_mw856067.fasta)"

# Extract sequence (remove header)
SEQUENCE=$(grep -v "^>" p54_mw856067.fasta | tr -d '\n')
HEADER=$(grep "^>" p54_mw856067.fasta)

echo "Header: $HEADER"
echo "Sequence length: $(echo -n "$SEQUENCE" | wc -c) aa"

# Check if sequence contains any gaps or non-standard chars
if echo "$SEQUENCE" | grep -q "[^ACDEFGHIKLMNPQRSTVWY]"; then
    echo "⚠️ WARNING: Non-standard characters found!"
    echo "$SEQUENCE" | grep -o "[^ACDEFGHIKLMNPQRSTVWY]" | head -5
else
    echo "✅ Sequence contains only standard amino acids"
fi

# Check if sequence starts with expected p54 N-terminus
if echo "$SEQUENCE" | grep -q "^MDSEFFQPVY"; then
    echo "✅ Sequence starts with expected p54 N-terminus (MDSEFFQPVY...)"
else
    echo "⚠️ Sequence does NOT start with expected p54 N-terminus"
    echo "First 20 aa: ${SEQUENCE:0:20}"
fi

# Save verified reference
echo "$HEADER" > "$OUTPUT_DIR/p54_reference.fasta"
echo "$SEQUENCE" >> "$OUTPUT_DIR/p54_reference.fasta"
echo "$SEQUENCE" > "$OUTPUT_DIR/p54_reference_clean.txt"

# SHA-256 checksum
SHA256=$(sha256sum "$OUTPUT_DIR/p54_reference.fasta" | awk '{print $1}')
echo "SHA-256: $SHA256"

# Clean up
rm -f p54_mw856067.fasta
