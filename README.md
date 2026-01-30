# TDA Donatoni – Lumen vs Nidi (Panel 1)

Pipeline:
1) Extract rests (inactive segments)
2) Verify segmentation invariants
3) Time-warp (active-time / compressed-silence)
4) Build embeddings
5) Run TDA

## Quickstart
```bash
python scripts/01_extract_rests.py --lumen data/derived/lumen/features.json --nidi data/derived/nidi1/features.json


