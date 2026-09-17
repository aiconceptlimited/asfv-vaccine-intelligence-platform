#!/bin/bash

echo "=========================================="
echo "P30 FINAL CANDIDATE RANKING"
echo "=========================================="
echo ""

echo "TIER 1: Strong binder + ≥3 alleles + 100% conserved"
grep "CONSERVED" p30_conservation_results.tsv | grep "Strong" | awk -F'\t' '$4 >= 3' | sort -t$'\t' -k4 -rn -k5 -n

echo ""
echo "TIER 2: Strong binder + ≥2 alleles + ≥90% conserved"
grep -E "CONSERVED|HIGHLY_CONSERVED" p30_conservation_results.tsv | grep "Strong" | awk -F'\t' '$4 >= 2' | sort -t$'\t' -k4 -rn -k5 -n

echo ""
echo "TIER 3: Strong binder but narrower breadth"
grep "Strong" p30_conservation_results.tsv | awk -F'\t' '$4 < 2' | sort -t$'\t' -k6 -rn -k4 -rn

echo ""
echo "TIER 4: Weak binder with exceptional breadth (>4 alleles) and good conservation"
grep "Weak" p30_conservation_results.tsv | awk -F'\t' '$4 >= 4' | grep -E "CONSERVED|HIGHLY_CONSERVED" | sort -t$'\t' -k4 -rn -k6 -rn
