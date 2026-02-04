# Segmentation verification report

- Generated at: `2026-02-04T16:12:46`
- Input: `/Users/alessandrocasali/Documents/Dottorato/Nidi/TDA_bis/results/rests_sequences.json`

## Summary

- Lumen rests: **19** (total **39.500** eighth)
- Nidi rests: **18** (total **35.500** eighth)
- Prefix match (eighth list): **0** / 18
- First mismatch at index 0: Lumen=1.0 vs Nidi=3.0 (delta=-2.0)

## Lumen

- Rests (count): **19**
- Total rest: **39.500** (eighth) = **19.750** (quarter)

### Rest durations (eighth units)
- min / max: 0.500 / 4.500
- mean / median: 2.079 / 1.500
- stdev: 1.480
- q25 / q50 / q75: 0.750 / 1.500 / 3.500

### Rest intervals (quarter units)
- intervals sorted & non-overlapping: **True**
- interval length min / max: 0.250 / 2.250

### Active gaps between rests (quarter units)
- internal gaps count: **18** (should be rests-1)
- gap min / max: 0.250 / 0.500
- gap mean / median: 0.292 / 0.250

### First 12 rests (eighth units)
`1.0, 4.0, 2.5, 0.5, 4.5, 1.0, 4.0, 1.5, 0.5, 1.5, 3.0, 3.0, ...`

## Nidi (Panel 1)

- Rests (count): **18**
- Total rest: **35.500** (eighth) = **17.750** (quarter)

### Rest durations (eighth units)
- min / max: 0.500 / 4.000
- mean / median: 1.972 / 1.500
- stdev: 1.241
- q25 / q50 / q75: 1.000 / 1.500 / 3.000

### Rest intervals (quarter units)
- intervals sorted & non-overlapping: **True**
- interval length min / max: 0.250 / 2.000

### Active gaps between rests (quarter units)
- internal gaps count: **17** (should be rests-1)
- gap min / max: 0.500 / 1.000
- gap mean / median: 0.647 / 0.500

### First 12 rests (eighth units)
`3.0, 2.5, 1.0, 3.5, 1.0, 4.0, 1.5, 0.5, 1.5, 3.0, 2.5, 0.5, ...`

## Comparison (Lumen vs Nidi)

- Rest count delta: **1**
- Total rest (eighth) delta: **4.000**
- First mismatch: {'index': 0, 'a': 1.0, 'b': 3.0, 'delta': -2.0}
