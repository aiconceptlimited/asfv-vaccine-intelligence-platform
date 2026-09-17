#!/bin/bash

REFERENCE_FILE="$1"
if [ -z "$REFERENCE_FILE" ]; then
    REFERENCE_FILE="/home/abubakar/asfv_vaccine_platform/data/processed/alignments/CP204L_p30_all_aligned.fasta"
fi

# Extract reference sequence (remove gaps, header)
REFSEQ=$(grep -v "^>" "$REFERENCE_FILE" | head -1 | tr -d '\n' | tr -d '-')

echo "Reference sequence length (ungapped): $(echo -n "$REFSEQ" | wc -c)"
echo ""
echo "=========================================="
echo "P30 CANDIDATE COORDINATE MAPPING"
echo "=========================================="
echo ""

# Create mapping file
echo -e "Peptide\tLength\tStart\tEnd\tSLA_Breadth\tBest_Rank\tBindLevel" > p30_candidates_with_coordinates.tsv

# Map each candidate
grep -E "^[A-Z]" p30_candidate_master_table.tsv | grep -v "^#" | while IFS=$'\t' read -r peptide length breadth alleles rank best_allele bindlevel cons var notes; do
    # Skip if peptide is empty
    [ -z "$peptide" ] && continue
    
    # Search for exact peptide in reference
    # Use grep -b to get byte offset
    pos=$(echo "$REFSEQ" | grep -b -o "$peptide" | head -1 | cut -d: -f1)
    
    if [ -n "$pos" ]; then
        start=$((pos + 1))
        end=$((start + length - 1))
        echo -e "${peptide}\t${length}\t${start}\t${end}\t${breadth}\t${rank}\t${bindlevel}"
    else
        # Try case-insensitive or with flexible matching
        echo -e "${peptide}\t${length}\tNOT_FOUND\tNOT_FOUND\t${breadth}\t${rank}\t${bindlevel}"
    fi
done >> p30_candidates_with_coordinates.tsv

echo "✅ Mapping complete! File: p30_candidates_with_coordinates.tsv"
echo ""
echo "Preview:"
head -10 p30_candidates_with_coordinates.tsv
