#!/bin/bash
RESULT_FILE="$1"
INPUT_FILE="P30_CP204L_NetMHCpan_Batch01_INPUT.txt"
INPUT_CHECKSUM="9de30bcbabe273bcddff8175c775272a8612c78badbca85eb4c8cb56db396bdb"

echo "=========================================="
echo "P30 RESULT VALIDATION v2 - PEPTIDE × ALLELE MATRIX"
echo "=========================================="

# Define expected alleles
EXPECTED_ALLELES=("SLA-1:0101" "SLA-1:0401" "SLA-1:1201" "SLA-2:0401" "SLA-3:0301" "SLA-3:0401")
EXPECTED_ALLELE_COUNT=6
EXPECTED_PEPTIDES=500
EXPECTED_TOTAL_ROWS=$((EXPECTED_PEPTIDES * EXPECTED_ALLELE_COUNT))

echo ""
echo "--- INPUT FILE VERIFICATION ---"
CURRENT_CHECKSUM=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
if [ "$CURRENT_CHECKSUM" != "$INPUT_CHECKSUM" ]; then
    echo "❌ INPUT FILE CHECKSUM MISMATCH!"
    echo "   Expected: $INPUT_CHECKSUM"
    echo "   Got:      $CURRENT_CHECKSUM"
    exit 1
fi
echo "✅ Input file checksum verified"

INPUT_PEPTIDES_FILE=$(mktemp)
cat "$INPUT_FILE" | sort > "$INPUT_PEPTIDES_FILE"
INPUT_COUNT=$(wc -l < "$INPUT_PEPTIDES_FILE")
echo "✅ Input peptides: $INPUT_COUNT (expected: $EXPECTED_PEPTIDES)"

echo ""
echo "--- RESULT FILE STRUCTURE ---"
TOTAL_ROWS=$(grep -E '^[[:space:]]*[0-9]+[[:space:]]+SLA-' "$RESULT_FILE" | wc -l)
echo "Total rows: $TOTAL_ROWS (expected: $EXPECTED_TOTAL_ROWS)"

if [ "$TOTAL_ROWS" -ne "$EXPECTED_TOTAL_ROWS" ]; then
    echo "❌ INCORRECT ROW COUNT"
    exit 1
fi
echo "✅ Row count correct"

echo ""
echo "--- ALLELE DISTRIBUTION ---"
for ALLELE in "${EXPECTED_ALLELES[@]}"; do
    COUNT=$(grep -E "^[[:space:]]*[0-9]+[[:space:]]+${ALLELE}" "$RESULT_FILE" | wc -l)
    echo "${ALLELE}: ${COUNT}"
    if [ "$COUNT" -ne "$EXPECTED_PEPTIDES" ]; then
        echo "   ❌ Expected: $EXPECTED_PEPTIDES"
        ALLELE_FAIL=1
    fi
done

if [ "$ALLELE_FAIL" -eq 1 ]; then
    echo "❌ ALLELE DISTRIBUTION INCORRECT"
    exit 1
fi
echo "✅ Allele distribution correct (500 each)"

echo ""
echo "--- FIRST PEPTIDE CHECK ---"
FIRST_PEPTIDE=$(grep -E '^[[:space:]]*[0-9]+[[:space:]]+SLA-' "$RESULT_FILE" | head -1 | awk '{print $3}')
echo "First peptide: $FIRST_PEPTIDE"
if [ "$FIRST_PEPTIDE" = "MKMEVIFK" ]; then
    echo "✅ First peptide is correct"
else
    echo "❌ First peptide is WRONG: $FIRST_PEPTIDE"
    exit 1
fi

echo ""
echo "--- P72 CONTAMINATION CHECK ---"
P72_MASGGAFC=$(grep -c "MASGGAFC" "$RESULT_FILE")
P72_KPDPEPTL=$(grep -c "KPDPEPTL" "$RESULT_FILE")
P72_QTFPRNGY=$(grep -c "QTFPRNGY" "$RESULT_FILE")
echo "MASGGAFC: $P72_MASGGAFC"
echo "KPDPEPTL: $P72_KPDPEPTL"
echo "QTFPRNGY: $P72_QTFPRNGY"

if [ "$P72_MASGGAFC" -eq 0 ] && [ "$P72_KPDPEPTL" -eq 0 ] && [ "$P72_QTFPRNGY" -eq 0 ]; then
    echo "✅ No p72 contamination detected"
else
    echo "❌ P72 CONTAMINATION DETECTED!"
    echo "   Forensic signature: $P72_MASGGAFC occurrences of MASGGAFC"
    echo "   This indicates the entire job was run against p72 peptides"
    exit 1
fi

echo ""
echo "--- PEPTIDE × ALLELE MATRIX VALIDATION ---"
# Extract all (peptide, allele) pairs
RESULT_PAIRS_FILE=$(mktemp)
grep -E '^[[:space:]]*[0-9]+[[:space:]]+SLA-' "$RESULT_FILE" | awk '{print $3, $2}' | sort > "$RESULT_PAIRS_FILE"

# Check each input peptide appears exactly 6 times (once per allele)
MISSING_PEPTIDES=0
EXTRA_PEPTIDES=0
INCORRECT_COUNT=0

for PEPTIDE in $(cat "$INPUT_PEPTIDES_FILE"); do
    COUNT=$(grep "^${PEPTIDE} " "$RESULT_PAIRS_FILE" | wc -l)
    if [ "$COUNT" -ne 6 ]; then
        echo "   ❌ $PEPTIDE: $COUNT occurrences (expected 6)"
        INCORRECT_COUNT=$((INCORRECT_COUNT + 1))
    fi
done

# Check for any peptides not in input
TOTAL_RESULT_PEPTIDES=$(awk '{print $1}' "$RESULT_PAIRS_FILE" | sort | uniq | wc -l)
if [ "$TOTAL_RESULT_PEPTIDES" -ne "$EXPECTED_PEPTIDES" ]; then
    echo "   ❌ Result contains $TOTAL_RESULT_PEPTIDES unique peptides (expected $EXPECTED_PEPTIDES)"
    EXTRA_PEPTIDES=1
fi

# Find any extra peptides
EXTRA_PEPTIDE_LIST=$(comm -13 "$INPUT_PEPTIDES_FILE" <(awk '{print $1}' "$RESULT_PAIRS_FILE" | sort | uniq))
if [ -n "$EXTRA_PEPTIDE_LIST" ]; then
    echo "   ❌ Extra peptides found:"
    echo "$EXTRA_PEPTIDE_LIST" | head -10
    EXTRA_PEPTIDES=1
fi

if [ "$INCORRECT_COUNT" -eq 0 ] && [ "$EXTRA_PEPTIDES" -eq 0 ]; then
    echo "✅ All peptides appear exactly 6 times (once per allele)"
    echo "✅ No extra peptides found"
else
    echo "❌ PEPTIDE × ALLELE MATRIX INCORRECT"
    exit 1
fi

echo ""
echo "--- FINAL VERDICT ---"
echo "✅✅✅ PASSED - VALID P30 RESULT"
echo ""
echo "Summary:"
echo "  - Input SHA-256: ${CURRENT_CHECKSUM}"
echo "  - Input peptides: ${INPUT_COUNT}"
echo "  - Total rows: ${TOTAL_ROWS}"
echo "  - Alleles: 6 (500 each)"
echo "  - p72 contamination: 0"
echo "  - All peptides × alleles: 1 occurrence each"
echo "  - Status: VALID P30 BATCH 1 RESULT"

# Cleanup
rm -f "$INPUT_PEPTIDES_FILE" "$RESULT_PAIRS_FILE"
exit 0
