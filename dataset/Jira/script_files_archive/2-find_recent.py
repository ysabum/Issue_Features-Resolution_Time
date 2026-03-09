'''
Script to narrow down issues to those that have been resolved in the recent past and have English language summary.
'''

import csv
import sys
from langdetect import detect, LangDetectException
import re

csv.field_size_limit(sys.maxsize)

# Get only the rows with a resolution date
with open('csv_files/issues.csv', mode='r', encoding='utf-8', newline='') as infile, \
     open('csv_files/1-issues_resolution.csv', mode='w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader((line.replace('\x00', '') for line in infile))
    writer = csv.writer(outfile)

    for row in reader:
        if len(row) > 4:
            # If the value is exactly 'NULL', skip
            if row[4].strip() != 'NULL':
                writer.writerow(row)


# Get only the rows with English language summary
with open('csv_files/1-issues_resolution.csv', mode='r', encoding='utf-8', newline='') as infile, \
     open('csv_files/2-issues_resolution_en.csv', mode='w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        if len(row) > 8:
            summary = row[8].strip()
            try:
                # Detect language of the summary
                language = detect(summary)
                if language == 'en':  # 'en' means English
                    writer.writerow(row)
            except LangDetectException:
                # If detection fails (e.g., empty summary), skip the row
                continue


# Get only the rows with a summary and description and a resolution date in the recent past
with open('csv_files/2-issues_resolution_en.csv', mode='r', encoding='utf-8', newline='') as infile, \
     open('csv_files/3-issues_recent.csv', mode='w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader((line.replace('\x00', '') for line in infile))
    writer = csv.writer(outfile)

    # Write header
    header = next(reader)
    writer.writerow(header)

    for row in reader:
        if len(row) > 9:  # Only process rows with at least 10 fields
            resolution_date = row[4].strip()
            summary = row[8].strip()
            description = row[9].strip()

            if resolution_date != 'NULL' and summary != 'NULL' and description != 'NULL':
                try:
                    match = re.search(r'\d{4}', resolution_date)

                    if match:
                        year = int(match.group())
                        if year > 2015:
                            writer.writerow(row)
                except ValueError:
                    continue  # Skip bad date rows