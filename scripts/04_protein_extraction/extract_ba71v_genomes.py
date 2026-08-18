#!/usr/bin/env python3
"""
Extract proteins from BA71V-annotated genomes (PQ375362, PQ375363)
"""

from Bio import SeqIO
import json
from pathlib import Path

# BA71V to standard gene name mapping
BA71V_GENES = {
    "BA71V-B646L": "B646L",
    "BA71V-CP204L": "CP204L",
    "BA71V-E183L": "E183L",
    "BA71V-EP402R": "EP402R",
    "BA71V-CP2475L": "CP2475L",
    "BA71V-CP312R": "CP312R",
}

# Genomes to process
BA71V_GENOMES = ["PQ375362", "PQ375363"]

def extract_proteins(gbff_path, accession):
    """Extract proteins from a BA71V-annotated GenBank file"""
    results = {}
    for record in SeqIO.parse(gbff_path, "genbank"):
        for feature in record.features:
            if feature.type == "CDS":
                # Check for BA71V gene names
                for ba71v_name, std_name in BA71V_GENES.items():
                    # Check in product, gene, and note fields
                    found = False
                    for qual in ["product", "gene", "note"]:
                        if qual in feature.qualifiers:
                            value = feature.qualifiers[qual][0]
                            if ba71v_name in value or ba71v_name.replace("BA71V-", "") in value:
                                found = True
                                break
                    
                    if found:
                        if "translation" in feature.qualifiers:
                            seq = feature.qualifiers["translation"][0]
                            results[std_name] = {
                                "accession": accession,
                                "gene": std_name,
                                "sequence": seq,
                                "length": len(seq),
                                "found": True,
                                "source": ba71v_name
                            }
                        break
    return results

def main():
    all_results = {}
    for accession in BA71V_GENOMES:
        gbff_path = f"data/raw/genomes/{accession}.gbff"
        if Path(gbff_path).exists():
            print(f"Processing {accession}...")
            all_results[accession] = extract_proteins(gbff_path, accession)
            for gene, data in all_results[accession].items():
                print(f"  {gene}: {data['length']} aa")
        else:
            print(f"File not found: {gbff_path}")
    
    # Save results
    with open("data/metadata/ba71v_extraction_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n✅ Extraction complete!")
    print(f"Results saved to: data/metadata/ba71v_extraction_results.json")
    
    # Generate FASTA files
    for accession, proteins in all_results.items():
        for gene, data in proteins.items():
            fasta_file = f"data/interim/proteins/BA71V_{gene}_{accession}.fasta"
            with open(fasta_file, "w") as f:
                f.write(f">{accession}_{gene} {gene} from {accession} (BA71V annotated)\n")
                f.write(f"{data['sequence']}\n")
            print(f"  Saved: {fasta_file}")

if __name__ == "__main__":
    main()
