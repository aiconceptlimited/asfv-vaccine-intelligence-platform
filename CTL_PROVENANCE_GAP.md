# CTL Panel Provenance Gap Report

## Issue
The transition from 8 CTL candidates to 3 final CTL epitopes is not documented.

## Evidence
- panel_v1.3_corrected_decisions.csv shows 6 candidates marked KEEP
- Only RSIPLANIY and KTLLSTVKY are marked REVIEW
- The final three (HIDKNIIQY, RSIPLANIY, YTDIVQKKY) do not correspond to any obvious selection rule

## Known Facts
1. HIDKNIIQY - KEEP, #3 in ranking, selected
2. RSIPLANIY - REVIEW, #4 in ranking, selected
3. YTDIVQKKY - KEEP, #7 in ranking, selected

## Excluded KEEP Candidates
1. SQWDLVQKF - #1 in ranking, KEEP, NOT selected
2. RVFSRLVFY - #2 in ranking, KEEP, NOT selected
3. SAMEVLHEL - #5 in ranking, KEEP, NOT selected
4. DRKHILMEF - #6 in ranking, KEEP, NOT selected

## Possible Explanations
1. Additional selection stage not captured in decision records
2. Manual selection without documented rationale
3. Inconsistent file versioning/harmonization
4. Different inclusion criteria applied (e.g., safety filtering after decision)

## Recommendation
Do NOT freeze the CTL panel until the 8→3 decision is fully documented.

