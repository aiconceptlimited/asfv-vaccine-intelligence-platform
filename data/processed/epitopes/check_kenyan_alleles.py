print("=" * 80)
print("CHECK CTL CANDIDATES AGAINST KENYAN ALLELES")
print("=" * 80)

print("""
### Instructions

1. Go to NetMHCpan-4.1: https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/

2. Submit the following peptides:
   - HIDKNIIQY
   - RSIPLANIY
   - YTDIVQKKY

3. Use custom SLA alleles:
   - SLA-1*1501
   - SLA-1*1502
   - SLA-2*NS#16
   - SLA-3*04hb06

4. Record binding predictions (EL score, %Rank)

5. Report results

### Expected Outcomes

If any peptide binds to Kenyan alleles:
  → Calculate population coverage using Kenyan frequencies
  → Keep current CTL panel

If no peptide binds to Kenyan alleles:
  → Current CTL panel has poor Kenyan coverage
  → Need to identify new CTL candidates for Kenyan populations
  → Re-run optimization with Kenyan alleles
""")
