import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

csv.field_size_limit(sys.maxsize)

input_path = BASE_DIR / "csvIntermediate" / "toxic-keywords-sample.csv"
output_path = BASE_DIR / "csvFiles" / "toxic-percent.csv"

with open(input_path, mode='r', encoding='utf-8', newline='') as infile, \
     open(output_path, mode='w', encoding='utf-8', newline='') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    writer.writerow([
        "created", "resolutiondate", "resolutiontime",
        "commentlength", "toxiclength", "percent_toxic"
    ])

    for row in reader:
        commentlength = int(row["commentlength"])
        toxic_keywords = row["toxic_keywords"] or ""
        toxiclength = len(toxic_keywords)

        percent_toxic = toxiclength / commentlength if commentlength > 0 else 0

        writer.writerow([
            row["created"],
            row["resolutiondate"],
            row["resolutiontime"],
            commentlength,
            toxiclength,
            percent_toxic
        ])