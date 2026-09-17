#!/usr/bin/env python3
"""
generate_architectures.py
Generates all 25,920 architectures with full QC verification
No selection - just enumeration and verification
"""

from itertools import permutations
import pandas as pd
import time
import json

# ============ FROZEN PARAMETERS ============
CTL_EPITOPES = ["HIDKNIIQY", "SAMEVLHEL", "YTDIVQKKY"]
HTL_EPITOPES = ["IVLIYLFSSRKKKAA", "RFIINIRSFKTVMTY", "KEEVRLMVIKLLKKK"]
BCELL_EPITOPES = [
    "LFEQEPSSETLKNTK", "RMNVVKKRDRDPCLQ", "TNSSVADRPVMNNPV",
    "AASAPSDELYTTATT", "NFQNEKHVGTISPST", "FTVKKNEQGEEIYPG"
]

LINKERS = {
    'ctl_ctl': 'AAY',
    'htl_htl': 'GPGPG',
    'bcell_bcell': 'GGS',
    'domain': 'EAAAK'
}

# Expected lengths
EXPECTED_CTL_LEN = 27 + 6  # 3x9 + 2x3 = 33
EXPECTED_HTL_LEN = 45 + 10  # 3x15 + 2x5 = 55
EXPECTED_BCELL_LEN = 90 + 15  # 6x15 + 5x3 = 105
EXPECTED_DOMAIN_LEN = 10  # 2x5
EXPECTED_TOTAL = 203

# ============ QC FUNCTIONS ============
def verify_epitopes_intact(sequence, epitopes):
    """Verify all epitopes are present and unchanged"""
    results = []
    for ep in epitopes:
        if ep in sequence:
            results.append({'epitope': ep, 'present': True, 'count': sequence.count(ep)})
        else:
            results.append({'epitope': ep, 'present': False, 'count': 0})
    return results

def verify_linkers(sequence):
    """Verify all linkers are correctly placed"""
    linkers_found = {}
    for name, linker in LINKERS.items():
        if name == 'domain':
            # Domain linkers appear twice
            count = sequence.count(linker)
            linkers_found[name] = {'linker': linker, 'count': count, 'expected': 2}
        else:
            count = sequence.count(linker)
            if name == 'ctl_ctl':
                expected = 2  # Between CTL1-CTL2 and CTL2-CTL3
            elif name == 'htl_htl':
                expected = 2  # Between HTL1-HTL2 and HTL2-HTL3
            elif name == 'bcell_bcell':
                expected = 5  # Between 6 B-cell epitopes
            else:
                expected = 0
            linkers_found[name] = {'linker': linker, 'count': count, 'expected': expected}
    return linkers_found

def build_architecture(ctl_order, htl_order, bcell_order):
    """Build a single architecture with full QC"""
    
    # Build blocks
    ctl_block = LINKERS['ctl_ctl'].join(ctl_order)
    htl_block = LINKERS['htl_htl'].join(htl_order)
    bcell_block = LINKERS['bcell_bcell'].join(bcell_order)
    
    # Full sequence
    full_sequence = ctl_block + LINKERS['domain'] + htl_block + LINKERS['domain'] + bcell_block
    
    # Calculate lengths
    ctl_len = len(ctl_block)
    htl_len = len(htl_block)
    bcell_len = len(bcell_block)
    total_len = len(full_sequence)
    
    # QC: Verify all epitopes are intact
    all_epitopes = CTL_EPITOPES + HTL_EPITOPES + BCELL_EPITOPES
    epitope_check = verify_epitopes_intact(full_sequence, all_epitopes)
    
    # QC: Verify linkers
    linker_check = verify_linkers(full_sequence)
    
    # Determine QC pass
    qc_pass = all(e['present'] for e in epitope_check)
    qc_pass = qc_pass and all(l['count'] == l['expected'] for l in linker_check.values())
    qc_pass = qc_pass and (total_len == EXPECTED_TOTAL)
    
    return {
        'ctl_block': ctl_block,
        'htl_block': htl_block,
        'bcell_block': bcell_block,
        'full_sequence': full_sequence,
        'lengths': {
            'ctl': ctl_len,
            'htl': htl_len,
            'bcell': bcell_len,
            'total': total_len
        },
        'qc': {
            'pass': qc_pass,
            'epitopes': epitope_check,
            'linkers': linker_check
        }
    }

# ============ GENERATE ALL ARCHITECTURES ============
print("=" * 70)
print("ASFV CONSTRUCT ARCHITECTURE GENERATOR")
print("=" * 70)
print("\n📋 Frozen parameters:")
print(f"   CTL epitopes: {len(CTL_EPITOPES)} (each 9 aa)")
print(f"   HTL epitopes: {len(HTL_EPITOPES)} (each 15 aa)")
print(f"   B-cell epitopes: {len(BCELL_EPITOPES)} (each 15 aa)")
print(f"   Linkers: AAY, GPGPG, GGS, EAAAK")
print(f"   Expected total length: {EXPECTED_TOTAL} aa")

# Generate permutations
print("\n🔢 Generating permutations...")
ctl_perms = list(permutations(CTL_EPITOPES))
htl_perms = list(permutations(HTL_EPITOPES))
bcell_perms = list(permutations(BCELL_EPITOPES))

print(f"   CTL: {len(ctl_perms)}")
print(f"   HTL: {len(htl_perms)}")
print(f"   B-cell: {len(bcell_perms):,}")
print(f"   Total architectures: {len(ctl_perms) * len(htl_perms) * len(bcell_perms):,}")

# Build all architectures
print("\n🏗️ Building all architectures...")
start_time = time.time()

architectures = []
failed_qc = []
idx = 0

for ctl_idx, ctl_order in enumerate(ctl_perms, 1):
    for htl_idx, htl_order in enumerate(htl_perms, 1):
        for bcell_idx, bcell_order in enumerate(bcell_perms, 1):
            arch = build_architecture(ctl_order, htl_order, bcell_order)
            
            architectures.append({
                'architecture_id': f"C{ctl_idx:02d}_H{htl_idx:02d}_B{bcell_idx:03d}",
                'ctl_order': '|'.join(ctl_order),
                'htl_order': '|'.join(htl_order),
                'bcell_order': '|'.join(bcell_order),
                'ctl_block': arch['ctl_block'],
                'htl_block': arch['htl_block'],
                'bcell_block': arch['bcell_block'],
                'full_sequence': arch['full_sequence'],
                'length_aa': arch['lengths']['total'],
                'ctl_len': arch['lengths']['ctl'],
                'htl_len': arch['lengths']['htl'],
                'bcell_len': arch['lengths']['bcell'],
                'qc_pass': arch['qc']['pass']
            })
            
            if not arch['qc']['pass']:
                failed_qc.append({
                    'id': f"C{ctl_idx:02d}_H{htl_idx:02d}_B{bcell_idx:03d}",
                    'reason': 'QC failed'
                })
            
            idx += 1
            if idx % 5000 == 0:
                print(f"   Built {idx:,} architectures...")

elapsed = time.time() - start_time
print(f"✅ Built {idx:,} architectures in {elapsed:.2f} seconds")

# ============ QC SUMMARY ============
print("\n📊 QC Summary:")
df = pd.DataFrame(architectures)

qc_passed = df['qc_pass'].sum()
qc_failed = len(df) - qc_passed
print(f"   QC Passed: {qc_passed:,}")
print(f"   QC Failed: {qc_failed:,}")

if qc_failed > 0:
    print(f"   ⚠️ WARNING: {qc_failed} architectures failed QC")
    print("   First 5 failures:")
    for f in failed_qc[:5]:
        print(f"      - {f['id']}")
else:
    print("   ✅ ALL architectures passed QC")

# Length verification
unique_lengths = df['length_aa'].unique()
print(f"\n📏 Length check:")
print(f"   Unique lengths: {sorted(unique_lengths)}")
if len(unique_lengths) == 1 and unique_lengths[0] == EXPECTED_TOTAL:
    print(f"   ✅ All {len(df):,} architectures are exactly {EXPECTED_TOTAL} aa")
else:
    print(f"   ⚠️ Length variation detected!")

# ============ SAVE OUTPUTS ============
print("\n💾 Saving outputs...")

# Main TSV
df.to_csv('construct_orders_all.tsv', sep='\t', index=False)
print(f"   ✅ construct_orders_all.tsv ({len(df):,} rows)")

# FASTA
with open('construct_orders_all.fasta', 'w') as f:
    for _, row in df.iterrows():
        f.write(f">{row['architecture_id']}|CTL:{row['ctl_order']}|HTL:{row['htl_order']}|B:{row['bcell_order']}\n")
        f.write(f"{row['full_sequence']}\n")
print(f"   ✅ construct_orders_all.fasta")

# Summary
summary = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'total_architectures': len(df),
    'ctl_permutations': len(ctl_perms),
    'htl_permutations': len(htl_perms),
    'bcell_permutations': len(bcell_perms),
    'expected_length': EXPECTED_TOTAL,
    'qc_passed': int(qc_passed),
    'qc_failed': int(qc_failed),
    'all_qc_pass': qc_failed == 0,
    'linkers': LINKERS,
    'epitopes': {
        'ctl': CTL_EPITOPES,
        'htl': HTL_EPITOPES,
        'bcell': BCELL_EPITOPES
    }
}

with open('construct_enumeration_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"   ✅ construct_enumeration_summary.json")

# ============ FINAL STATUS ============
print("\n" + "=" * 70)
print("✅ ENUMERATION COMPLETE")
print("=" * 70)
print(f"\n📋 Candidate table generated:")
print(f"   - {len(df):,} architectures")
print(f"   - All 203 aa")
print(f"   - All 12 epitopes intact")
print(f"   - All linkers correctly placed")
print(f"   - QC: {'ALL PASSED ✅' if qc_failed == 0 else f'{qc_failed} FAILED ⚠️'}")

print(f"\n🔬 Next scientific step:")
print("   Generate junction peptides for SLA-I/SLA-II screening")
print("\n📁 Output files:")
print("   • construct_orders_all.tsv")
print("   • construct_orders_all.fasta")
print("   • construct_enumeration_summary.json")
