"""Add ALL phrases from the PDF to the knowledge graph as leadership traits.

This script reads the "Fifteen Thousand Useful Phrases" text file and adds
ALL phrases to the V-LKG knowledge graph as leadership traits and characterization points.
Optimized for large datasets with batch saving.
"""

import json
import os
import sys
import re
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.database.local_graph import LocalGraphStore


def extract_all_phrases_from_text(text_path):
    """Extract all phrases from the PDF text file."""
    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()

    phrases = []

    # Extract phrases from different sections
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
            # These sections contain adjective+noun or noun+and+noun phrases
            if re.match(r'^[a-z][a-z\s\-\']+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s\-\']+ and [a-z\s\-\']+$', line):
                phrases.append((line, current_section))
            elif re.match(r'^[a-z][a-z\s\-\']+, [a-z\s\-\']+, and [a-z\s\-\']+$', line):
                phrases.append((line, current_section))

        elif current_section == 'PREPOSITIONAL':
            # Prepositional phrases like "abandon of spontaneity"
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
            # Literary expressions - longer descriptive phrases
            if re.match(r'^[A-Z][a-z].*$', line) and len(line) > 20:
                phrases.append((line, current_section))

        elif current_section == 'SIMILES':
            # Similes starting with "like" or "as"
            if line.lower().startswith('like ') or line.lower().startswith('as '):
                phrases.append((line, current_section))

        elif current_section in ['CONVERSATIONAL', 'PUBLIC_SPEAKING', 'MISCELLANEOUS']:
            # These contain various phrase types
            if len(line) > 10 and not line.startswith('A ') and not line.startswith('I '):
                phrases.append((line, current_section))

    return phrases


def add_all_phrases_to_knowledge_graph(text_path):
    """Add ALL phrases from the PDF to the knowledge graph."""
    print(f"Reading phrases from: {text_path}")

    # Extract all phrases
    phrases = extract_all_phrases_from_text(text_path)
    print(f"Extracted {len(phrases)} phrases from the document")

    # Initialize the local graph store
    store = LocalGraphStore()
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Add the document itself as a reference
    store.insert_triplet(
        "Fifteen Thousand Useful Phrases",
        "ReferenceDocument",
        "HAS_AUTHOR",
        "Grenville Kleiser",
        "Author",
        source_time=timestamp,
        video_id="pdf_reference"
    )

    store.insert_triplet(
        "Fifteen Thousand Useful Phrases",
        "ReferenceDocument",
        "HAS_CATEGORY",
        "Language & Communication",
        "Category",
        source_time=timestamp,
        video_id="pdf_reference"
    )

    store.insert_triplet(
        "Fifteen Thousand Useful Phrases",
        "ReferenceDocument",
        "HAS_PURPOSE",
        "Leadership Communication & Expression",
        "Purpose",
        source_time=timestamp,
        video_id="pdf_reference"
    )

    # Add all phrases as leadership traits and characterization points
    print("\nAdding phrases to knowledge graph...")

    # Process in batches to avoid memory issues
    batch_size = 500
    total_added = 0

    for i in range(0, len(phrases), batch_size):
        batch = phrases[i:i+batch_size]

        for phrase, section in batch:
            # All phrases are treated as leadership traits and characterization points
            store.insert_triplet(
                phrase,
                "LeadershipTrait",
                "EXTRACTED_FROM",
                "Fifteen Thousand Useful Phrases",
                "ReferenceDocument",
                source_time=timestamp,
                video_id="pdf_reference"
            )

            store.insert_triplet(
                phrase,
                "LeadershipTrait",
                "BELONGS_TO",
                section,
                "PhraseCategory",
                source_time=timestamp,
                video_id="pdf_reference"
            )

            store.insert_triplet(
                phrase,
                "LeadershipTrait",
                "SUPPORTS",
                "Leadership Communication",
                "Competency",
                source_time=timestamp,
                video_id="pdf_reference"
            )

            store.insert_triplet(
                phrase,
                "LeadershipTrait",
                "CHARACTERIZES",
                "Leadership Personality",
                "Personality",
                source_time=timestamp,
                video_id="pdf_reference"
            )

            total_added += 1

        print(f"  Added {total_added}/{len(phrases)} phrases...")

        # Save after each batch
        store._save()

    print(f"\n✅ Successfully added {len(phrases)} phrases to the knowledge graph!")

    # Get updated stats
    stats = store.get_stats()
    print(f"\n📊 Updated Knowledge Graph Stats:")
    print(f"   - Nodes: {stats['node_count']}")
    print(f"   - Relationships: {stats['rel_count']}")
    print(f"   - Avg Degree: {stats['avg_degree']}")


if __name__ == "__main__":
    text_path = r"C:\Users\gopic\Downloads\Fifteen-Thousand-Useful-Phrases.txt"

    if not os.path.exists(text_path):
        print(f"❌ File not found: {text_path}")
        print("Please make sure the text file exists at the specified path.")
        sys.exit(1)

    add_all_phrases_to_knowledge_graph(text_path)
