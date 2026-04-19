import csv
import random
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

input_path = BASE_DIR / "csvIntermediate" / "6-issues_analyzed.csv"
output_path = BASE_DIR / "csvIntermediate" / "6.1-issues_analyzed_sample.csv"

csv.field_size_limit(sys.maxsize)

# Load all rows
with open(input_path, mode='r', encoding='utf-8', newline='') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# Separate rows by tone type
non_neutral = [r for r in rows if r["tone_keywords"].strip() != ""]
neutral = [r for r in rows if r["tone_keywords"].strip() == ""]

# Sampling logic
if len(non_neutral) >= 250:
    selected_non_neutral = random.sample(non_neutral, 250)
    selected_neutral = random.sample(neutral, 250)
    sample = selected_non_neutral + selected_neutral
else:
    selected_non_neutral = non_neutral
    needed = 380 - len(selected_non_neutral)
    selected_neutral = random.sample(neutral, needed)
    sample = selected_non_neutral + selected_neutral

random.shuffle(sample)

# Write sampled rows
with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)

    writer.writerow([
        'id', 'key', 'self', 'resolutiondate', 'created',
        'resolutiontime', 'timespent', 'titlelength', 'commentlength',
        'tone', 'tone_keywords', 'relevance', 'relevant_keywords'
    ])

    for row in sample:
        writer.writerow([
            row['id'], row['key'], row['self'],
            row['resolutiondate'], row['created'],
            row['resolutiontime'], row['timespent'],
            row['titlelength'], row['commentlength'],
            row['tone'], row['tone_keywords'],
            row['relevance'], row['relevant_keywords']
        ])