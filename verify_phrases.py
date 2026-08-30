import json

# Load the data
with open('data/processed/triplets.json', 'r', encoding='utf-8') as f:
    triplets = json.load(f)

# Find some good leadership trait examples
leadership_examples = [t for t in triplets if t.get('subject_type') == 'LeadershipTrait' and t.get('relation') == 'CHARACTERIZES']
print('=== LEADERSHIP TRAIT EXAMPLES ===')
for i, t in enumerate(leadership_examples[:30]):
    print(f'{i+1}. {t["subject"]}')

print(f'... and {len(leadership_examples) - 30} more leadership traits')

# Count by section
from collections import Counter
sections = Counter(t.get('object') for t in triplets if t.get('relation') == 'BELONGS_TO')
print('\n=== PHRASES BY SECTION ===')
for section, count in sections.most_common():
    print(f'  {section}: {count}')
