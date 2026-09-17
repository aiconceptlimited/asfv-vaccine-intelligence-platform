#!/bin/bash
# DeepTMHMM web server: https://dtu.biolib.com/DeepTMHMM

echo "⚠️  DeepTMHMM requires manual submission to:"
echo "https://dtu.biolib.com/DeepTMHMM"
echo ""
echo "Submit these protein files:"
for f in data/interim/proteins/*.fasta; do
    echo "  - $f"
done
