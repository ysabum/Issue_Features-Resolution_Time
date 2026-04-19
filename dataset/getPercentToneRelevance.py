import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

input_path = BASE_DIR / "csvIntermediate" / "6.1-issues_analyzed_sample.csv"
output_path = BASE_DIR / "csvIntermediate" / "6.2-issue_calculations.csv"

csv.field_size_limit(sys.maxsize)

with open(input_path, mode='r', encoding='utf-8', newline='') as infile, \
     open(output_path, mode='w', encoding='utf-8', newline='') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    writer.writerow([
        'id', 'key', 'self', 'resolutiondate', 'created',
        'resolutiontime', 'timespent', 'titlelength', 'commentlength',
        '%tone', '%relevance'
    ])

    for row in reader:
        try:
            title_length = int(row['titlelength'])
            comment_length = int(row['commentlength'])

            tone_keywords = row['tone_keywords'] or ""
            relevant_keywords = row['relevant_keywords'] or ""

            tone_len = len(tone_keywords)
            rel_len = len(relevant_keywords)

            pct_tone = tone_len / comment_length if comment_length > 0 else 0
            pct_relevance = rel_len / title_length if title_length > 0 else 0

            writer.writerow([
                row['id'], row['key'], row['self'],
                row['resolutiondate'], row['created'],
                row['resolutiontime'], row['timespent'],
                title_length, comment_length,
                pct_tone, pct_relevance
            ])

        except Exception as e:
            print(f"Error processing row: {e}")
            continue