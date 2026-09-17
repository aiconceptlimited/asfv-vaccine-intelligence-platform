#!/bin/bash

REFERENCE_FILE="p30_reference_full.fasta"

# Extract reference sequence (remove gaps)
REFSEQ=$(grep -v "^>" "$REFERENCE_FILE" | tr -d '\n' | tr -d '-')

echo "Reference sequence length (ungapped): $(echo -n "$REFSEQ" | wc -c)"
echo ""
echo "=========================================="
echo "P30 CANDIDATE COORDINATE MAPPING (FULL)"
echo "=========================================="
echo ""

# Create mapping file
echo -e "Peptide\tLength\tStart\tEnd\tSLA_Breadth\tBest_Rank\tBindLevel" > p30_candidates_with_coordinates_full.tsv

# Map each candidate
grep -E "^[A-Z]" p30_candidate_master_table.tsv | grep -v "^#" | while IFS=$'\t' read -r peptide length breadth alleles rank best_allele bindlevel cons var notes; do
    [ -z "$peptide" ] && continue
    
    # Search for exact peptide in reference
    pos=$(echo "$REFSEQ" | grep -b -o "$peptide" | head -1 | cut -d: -f1)
    
    if [ -n "$pos" ]; then
        start=$((pos + 1))
        end=$((start + length - 1))
        echo -e "${peptide}\t${length}\t${start}\t${end}\t${breadth}\t${rank}\t${bindlevel}"
    else
        echo -e "${peptide}\t${length}\tNOT_FOUND\tNOT_FOUND\t${breadth}\t${rank}\t${bindlevel}"
    fi
done >> p30_candidates_with_coordinates_full.tsv

echo "✅ Mapping complete! File: p30_candidates_with_coordinates_full.tsv"
echo ""
echo "Preview:"
head -10 p30_candidates_with_coordinates_full.tsv
