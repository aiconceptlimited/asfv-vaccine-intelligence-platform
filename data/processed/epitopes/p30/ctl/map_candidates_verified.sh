#!/bin/bash

REFSEQ=$(cat mw856067_sequence.txt)
REF_LEN=$(echo -n "$REFSEQ" | wc -c)

echo "=========================================="
echo "STAGE B: CANDIDATE MAPPING"
echo "=========================================="
echo "Reference: MW856067_CP204L"
echo "Length: $REF_LEN aa"
echo ""

# Create mapping table with QC columns
echo -e "Peptide\tLength\tStart\tEnd\tSLA_Breadth\tAlleles\tBest_Rank\tBest_Allele\tBindLevel\tMapping_Status" > p30_mapped_final.tsv

TOTAL=0
MAPPED=0
UNMAPPED=0
DUPLICATE=0

grep -E "^[A-Z]" p30_candidate_master_table.tsv | grep -v "^#" | while IFS=$'\t' read -r peptide length breadth alleles rank best_allele bindlevel cons var notes; do
    [ -z "$peptide" ] && continue
    TOTAL=$((TOTAL + 1))
    
    # Get actual peptide length from sequence
    ACTUAL_LEN=$(echo -n "$peptide" | wc -c)
    
    # Find all occurrences
    OCCURRENCES=$(echo "$REFSEQ" | grep -b -o "$peptide" | cut -d: -f1)
    OCC_COUNT=$(echo "$OCCURRENCES" | grep -c .)
    
    if [ "$OCC_COUNT" -eq 0 ]; then
        echo -e "${peptide}\t${ACTUAL_LEN}\t-\t-\t${breadth}\t${alleles}\t${rank}\t${best_allele}\t${bindlevel}\tUNMAPPED"
        UNMAPPED=$((UNMAPPED + 1))
    elif [ "$OCC_COUNT" -eq 1 ]; then
        pos=$(echo "$OCCURRENCES" | head -1)
        start=$((pos + 1))
        end=$((start + ACTUAL_LEN - 1))
        echo -e "${peptide}\t${ACTUAL_LEN}\t${start}\t${end}\t${breadth}\t${alleles}\t${rank}\t${best_allele}\t${bindlevel}\tMAPPED"
        MAPPED=$((MAPPED + 1))
    else
        # Multiple occurrences - report all
        FIRST_POS=$(echo "$OCCURRENCES" | head -1)
        start=$((FIRST_POS + 1))
        end=$((start + ACTUAL_LEN - 1))
        echo -e "${peptide}\t${ACTUAL_LEN}\t${start}\t${end}\t${breadth}\t${alleles}\t${rank}\t${best_allele}\t${bindlevel}\tDUPLICATE_${OCC_COUNT}"
        DUPLICATE=$((DUPLICATE + 1))
    fi
done >> p30_mapped_final.tsv

echo ""
echo "=== MAPPING RESULTS ==="
echo "Total candidates: $(tail -n +2 p30_mapped_final.tsv | wc -l)"
echo "Mapped: $(grep -c "MAPPED" p30_mapped_final.tsv)"
echo "Unmapped: $(grep -c "UNMAPPED" p30_mapped_final.tsv)"
echo "Duplicate occurrences: $(grep -c "DUPLICATE" p30_mapped_final.tsv)"

echo ""
echo "=== MAPPED CANDIDATES ==="
grep "MAPPED" p30_mapped_final.tsv | sort -t$'\t' -k5 -rn -k7 -n | head -10

echo ""
echo "=== UNMAPPED CANDIDATES (NEED REVIEW) ==="
grep "UNMAPPED" p30_mapped_final.tsv | cut -f1,5,6,9
