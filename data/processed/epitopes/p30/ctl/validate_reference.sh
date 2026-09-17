#!/bin/bash

echo "=========================================="
echo "STAGE A: REFERENCE VALIDATION"
echo "=========================================="

# 1. Extract MW856067 from alignment
ALIGNMENT="/home/abubakar/asfv_vaccine_platform/data/processed/alignments/CP204L_p30_all_aligned.fasta"

echo "1. Extracting MW856067 from alignment..."
awk '/^>MW856067/{flag=1; print; next} /^>/{flag=0} flag' "$ALIGNMENT" > mw856067_aligned.fasta

# Remove gaps to get protein sequence
REFSEQ=$(grep -v "^>" mw856067_aligned.fasta | tr -d '\n' | tr -d '-')
echo "MW856067 length (ungapped): $(echo -n "$REFSEQ" | wc -c) aa"
echo "$REFSEQ" > mw856067_sequence.txt

# 2. Find original p30 reference
echo ""
echo "2. Locating original p30 FASTA..."
ORIGINAL=$(find ~/asfv_vaccine_platform -name "*.fasta" -exec grep -l "CP204L" {} \; 2>/dev/null | head -3)

for f in $ORIGINAL; do
    echo "  Found: $f"
    ORIG_LEN=$(grep -v "^>" "$f" | tr -d '\n' | wc -c)
    echo "    Length: $ORIG_LEN aa"
done

# 3. Compare sequences if original exists
if [ -n "$ORIGINAL" ]; then
    echo ""
    echo "3. Comparing sequences..."
    ORIGSEQ=$(grep -v "^>" "$ORIGINAL" | tr -d '\n' | head -1)
    
    if [ "$REFSEQ" = "$ORIGSEQ" ]; then
        echo "✅ MW856067 matches original reference sequence"
    else
        echo "❌ SEQUENCE MISMATCH!"
        echo "MW856067: ${REFSEQ:0:50}..."
        echo "Original: ${ORIGSEQ:0:50}..."
    fi
fi

echo ""
echo "4. Checking known p30 motifs in MW856067:"
for motif in "MKMEVIFK" "KTLLSTVKY" "KAVQHIEQY" "RAHNYIQTI"; do
    count=$(echo "$REFSEQ" | grep -c "$motif")
    echo "  $motif: $count"
done

echo ""
echo "✅ Reference validation complete"
