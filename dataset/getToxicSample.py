import csv
import random
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

csv.field_size_limit(sys.maxsize)

input_path = BASE_DIR / "csvIntermediate" / "toxic-keywords.csv"
output_path = BASE_DIR / "csvIntermediate" / "toxic-keywords-sample.csv"

SAMPLE_SIZE = 360

# Load all rows
with open(input_path, mode='r', encoding='utf-8', newline='') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# Random sample (handles case where fewer than 340 rows exist)
sample_size = min(SAMPLE_SIZE, len(rows))
sample = random.sample(rows, sample_size)

# Write sampled rows
with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)

    # Write header exactly as in input
    writer.writerow(reader.fieldnames)

    # Write sampled rows
    for row in sample:
        writer.writerow([row[field] for field in reader.fieldnames])