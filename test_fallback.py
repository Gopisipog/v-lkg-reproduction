"""Test fallback extractor with per-video concatenation."""
import json, os
os.chdir(r"D:\v_lkg_reproduction")
from src.core.fallback_extractor import batch_extract, batch_extract_entities

with open("data/processed/corpus.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

triplets = batch_extract(corpus)
print(f"Total unique triplets: {len(triplets)}")

types = {}
for t in triplets:
    for role in ["subject_type", "object_type"]:
        tp = t[role]
        types[tp] = types.get(tp, 0) + 1
print("Entity types found:")
for k, v in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print("\nSample triplets (first 20):")
for t in triplets[:20]:
    s, r, o = t["subject"], t["relation"], t["object"]
    st, ot = t["subject_type"], t["object_type"]
    print(f"  ({s}) -[{r}]-> ({o})  [{st}->{ot}]")

entities = batch_extract_entities(corpus)
print(f"\nUnique entities: {len(entities)}")
by_type = {}
for e in entities:
    by_type[e["type"]] = by_type.get(e["type"], 0) + 1
print("By type:")
for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print("\nAll entities:")
for e in entities:
    print(f"  {e['name']} ({e['type']})")
