#!/bin/bash
# SignalP-6.0 needs to be downloaded separately
# Or use web server: https://services.healthtech.dtu.dk/services/SignalP-6.0/

echo "⚠️  SignalP-6.0 requires manual download from:"
echo "https://services.healthtech.dtu.dk/services/SignalP-6.0/"
echo ""
echo "Or submit proteins manually:"
for f in data/interim/proteins/*.fasta; do
    echo "  - Submit: $f"
done
