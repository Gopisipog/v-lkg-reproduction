"""Add ALL phrases from the PDF to the knowledge graph as leadership traits.

Fast version - builds all data in memory first, then saves once.
"""

import json
import os
import sys
import re
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))


def extract_all_phrases_from_text(text_path):
    """Extract all phrases from the PDF text file."""
    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()

    phrases = []
    lines = content.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()

        # Track sections
        if 'SECTION I' in line:
            current_section = 'USEFUL'
            continue
        elif 'SECTION II' in line:
            current_section = 'SIGNIFICANT'
            continue
        elif 'SECTION III' in line:
            current_section = 'FELICITOUS'
            continue
        elif 'SECTION IV' in line:
            current_section = 'IMPRESSIVE'
            continue
        elif 'SECTION V' in line:
            current_section = 'PREPOSITIONAL'
            continue
        elif 'SECTION VI' in line:
            current_section = 'BUSINESS'
            continue
        elif 'SECTION VII' in line:
            current_section = 'LITERARY'
            continue
        elif 'SECTION VIII' in line:
            current_section = 'SIMILES'
            continue
        elif 'SECTION IX' in line:
            current_section = 'CONVERSATIONAL'
            continue
        elif 'SECTION X' in line:
            current_section = 'PUBLIC_SPEAKING'
            continue
        elif 'SECTION XI' in line:
            current_section = 'MISCELLANEOUS'
            continue

        # Skip empty lines, headers, page numbers, etc.
        if not line or len(line) < 3:
            continue
        if line.startswith('Fifteen Thousand') or line.startswith('Open Education'):
            continue
        if line.startswith('OKFN') or line.startswith('GRENVILLE'):
            continue
        if line.isdigit():
            continue
        if line.startswith('[') and line.endswith(']'):
            continue

        # Extract phrases based on section
        if current_section in ['USEFUL', 'SIGNIFICANT', 'FELICITOUS', 'IMPRESSIVE']:
            if re.match(r'^[a-z][a-z\s\-\']+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s\-\']+ and [a-z\s\-\']+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s\-\']+, [a-z\s\-\']+, and [a-z\s\-\']+$', line):
                phrases.append((line, current_section))

        elif current_section == 'PREPOSITIONAL':
            if re.match(r'^[a-z][a-z\s]+ of [a-z\s]+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s]+ by [a-z\s]+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s]+ in [a-z\s]+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s]+ into [a-z\s]+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s]+ to [a-z\s]+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s]+ with [a-z\s]+$', line):
                phrases.append((line, current_section))

        elif current_section == 'LITERARY':
            if re.match(r'^[A-Z][a-z].*$', line) and len(line) > 20:
                phrases.append((line, current_section))

        elif current_section == 'SIMILES':
            if line.lower().startswith('like ') or line.lower().startswith('as '):
                phrases.append((line, current_section))

        elif current_section in ['CONVERSATIONAL', 'PUBLIC_SPEAKING', 'MISCELLANEOUS']:
            if len(line) > 10 and not line.startswith('A ') and not line.startswith('I '):
                phrases.append((line, current_section))

    return phrases


def add_all_phrases_fast(text_path):
    """Add ALL phrases from the PDF to the knowledge graph - fast version."""
    print(f"Reading phrases from: {text_path}")

    # Extract all phrases
    phrases = extract_all_phrases_from_text(text_path)
    print(f"Extracted {len(phrases)} phrases from the document")

    # Load existing data
    triplets_path = "data/processed/triplets.json"
    entities_path = "data/processed/entities.json"

    # Load existing triplets
    existing_triplets = []
    if os.path.exists(triplets_path):
        try:
            with open(triplets_path, 'r', encoding='utf-8') as f:
                existing_triplets = json.load(f)
        except:
            existing_triplets = []

    # Load existing entities
    existing_entities = {}
    if os.path.exists(entities_path):
        try:
            with open(entities_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                for e in raw:
                    existing_entities[e.get('name', '')] = e
        except:
            existing_entities = {}

    timestamp = datetime.utcnow().isoformat() + "Z"
    new_triplets = []

    # Add document metadata triplets
    doc_triplets = [
        ("Fifteen Thousand Useful Phrases", "ReferenceDocument", "HAS_AUTHOR", "Grenville Kleiser", "Author"),
        ("Fifteen Thousand Useful Phrases", "ReferenceDocument", "HAS_CATEGORY", "Language & Communication", "Category"),
        ("Fifteen Thousand Useful Phrases", "ReferenceDocument", "HAS_PURPOSE", "Leadership Communication & Expression", "Purpose"),
    ]
    new_triplets.extend(doc_triplets)

    # Add all phrases
    print("\nBuilding triplets...")
    for phrase, section in phrases:
        # EXTRACTED_FROM
        new_triplets.append((
            phrase, "LeadershipTrait", "EXTRACTED_FROM",
            "Fifteen Thousand Useful Phrases", "ReferenceDocument"
        ))
        # BELONGS_TO
        new_triplets.append((
            phrase, "LeadershipTrait", "BELONGS_TO",
            section, "PhraseCategory"
        ))
        # SUPPORTS
        new_triplets.append((
            phrase, "LeadershipTrait", "SUPPORTS",
            "Leadership Communication", "Competency"
        ))
        # CHARACTERIZES
        new_triplets.append((
            phrase, "LeadershipTrait", "CHARACTERIZES",
            "Leadership Personality", "Personality"
        ))

    # Convert to dict format
    print("Converting to dict format...")
    triplet_dicts = []
    for s, st, r, o, ot in new_triplets:
        triplet_dicts.append({
            "subject": s,
            "subject_type": st,
            "relation": r,
            "object": o,
            "object_type": ot,
            "source_time": timestamp,
            "video_ids": ["pdf_reference"],
            "weight": 1
        })

        # Add to entities
        if s not in existing_entities:
            existing_entities[s] = {
                "name": s,
                "type": st,
                "color": "#9C27B0",  # LeadershipTrait color
                "first_seen": timestamp,
                "video_ids": ["pdf_reference"]
            }
        if o not in existing_entities:
            existing_entities[o] = {
                "name": o,
                "type": ot,
                "color": "#607D8B",  # Default color
                "first_seen": timestamp,
                "video_ids": ["pdf_reference"]
            }

    # Merge with existing
    all_triplets = existing_triplets + triplet_dicts
    all_entities = list(existing_entities.values())

    # Save once
    print(f"Saving {len(all_triplets)} triplets and {len(all_entities)} entities...")
    os.makedirs("data/processed", exist_ok=True)

    with open(triplets_path, 'w', encoding='utf-8') as f:
        json.dump(all_triplets, f, indent=2, ensure_ascii=False)

    with open(entities_path, 'w', encoding='utf-8') as f:
        json.dump(all_entities, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Successfully added {len(phrases)} phrases to the knowledge graph!")
    print(f"   - Total triplets: {len(all_triplets)}")
    print(f"   - Total entities: {len(all_entities)}")
    print(f"   - New phrases added: {len(phrases)}")


if __name__ == "__main__":
    text_path = r"C:\Users\gopic\Downloads\Fifteen-Thousand-Useful-Phrases.txt"

    if not os.path.exists(text_path):
        print(f"❌ File not found: {text_path}")
        sys.exit(1)

    add_all_phrases_fast(text_path)
