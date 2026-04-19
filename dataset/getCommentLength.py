'''
Script to get the issue comment length of sample csv.
'''

#!/usr/bin/env python
import os
import csv
import sys
from datetime import datetime
from pathlib import Path

csv.field_size_limit(sys.maxsize)

BASE_DIR = Path(__file__).resolve().parent
MAX_CHARS = 6000

with open(BASE_DIR / 'csvIntermediate' / '5-issues_sample.csv', mode='r', encoding='utf-8', newline='') as infile, \
     open(BASE_DIR / 'csvIntermediate' / '6-issues_analyzed.csv', mode='w', encoding='utf-8', newline='') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write new header with selected fields
    writer.writerow([
        'id', 'key', 'self', 'resolutiondate', 'created', 
        'resolutiontime', 'timespent', 'commentlength', 
        'tone', 'relevance', 'descriptive'
    ])

    next(reader)  # Skip header row

    for row in reader:
        if len(row) > 24 and row[9].strip():
            summary = row[8].strip()
            description = row[9].strip()
            resolution_date_str = row[4].strip().strip('"').strip("'")
            created_date_str = row[5].strip().strip('"').strip("'")
            timespent = int(row[24].strip())

            # Truncate description if too long
            text = f"{summary}\n\n{description}"
            if len(text) > MAX_CHARS:
                description = description[:MAX_CHARS - len(summary)]

            try:
                resolution_date = datetime.strptime(resolution_date_str[:19], '%Y-%m-%dT%H:%M:%S')
                created_date = datetime.strptime(created_date_str[:19], '%Y-%m-%dT%H:%M:%S')
                resolution_time = (resolution_date - created_date).days
                comment_length = len(description)

                # Write row with empty tone/relevance/descriptive
                writer.writerow([
                    row[0],       # id
                    row[1],       # key
                    row[2],       # self
                    row[4],       # resolutiondate
                    row[5],       # created
                    resolution_time,
                    row[24],      # timespent
                    comment_length,
                    '',           # tone
                    '',           # relevance
                    ''            # descriptive
                ])

            except Exception as e:
                print(f"Error processing row: {e}")
                continue