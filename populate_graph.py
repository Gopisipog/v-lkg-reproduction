"""Populate the local graph store from the corpus using the fallback extractor."""
import json, os
os.chdir(r"D:\v_lkg_reproduction")

from src.core.fallback_extractor import batch_extract
from src.database.local_graph import LocalGraphStore

# load corpus
with open("data/processed/corpus.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

print(f"Loaded {len(corpus)} segments")

# extract triplets
triplets = batch_extract(corpus)
print(f"Extracted {len(triplets)} unique triplets")

# create graph store and insert
store = LocalGraphStore()
for t in triplets:
    store.insert_triplet(
        subject=t["subject"],
        subject_type=t["subject_type"],
        relation=t["relation"],
        obj=t["object"],
        obj_type=t["object_type"],
        video_id="batch_extract",
    )

print(f"\nGraph store now has:")
print(f"  Entities: {len(store.entities)}")
print(f"  Triplets: {len(store.triplets)}")

# show entity breakdown
by_type = {}
for e in store.entities.values():
    tp = e.get("type", "?")
    by_type[tp] = by_type.get(tp, 0) + 1
print("  By type:")
for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"    {k}: {v}")

# verify files exist
import os
for path in ["data/processed/entities.json", "data/processed/triplets.json"]:
    size = os.path.getsize(path)
    print(f"\n{path}: {size} bytes")
