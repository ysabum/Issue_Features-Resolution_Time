'''
Script to fix broken description delimiter in sample dataset.
'''

import csv
import sys
import random
from collections import defaultdict
from datetime import datetime

csv.field_size_limit(sys.maxsize)

# # Clean up the sample dataset
# input_file = 'csv_files/3-issues_recent.csv'
# output_file = 'csv_files/4-issues_recent_cleaned.csv'

# with open(input_file, mode='r', encoding='utf-8', newline='') as infile, \
#      open(output_file, mode='w', encoding='utf-8', newline='') as outfile:

#     reader = csv.reader((line.replace('\x00', '') for line in infile))
#     writer = csv.writer(outfile)

#     header = next(reader)
#     writer.writerow(header)

#     for row in reader:
#         if len(row) <= 12:
#             writer.writerow(row)  # row is likely fine
#             continue

#         fixed_row = row[:9]  # everything up to description
#         i = 9

#         reconstructed_description = row[i]
#         while True:
#             if i + 3 < len(row) and row[i + 1].strip() == 'NULL' and row[i + 2].strip() == 'NULL' and row[i + 3].strip() != 'NULL':
#                 # End of broken description
#                 break
#             if i + 1 >= len(row):
#                 break
#             reconstructed_description += ',' + row[i + 1]
#             i += 1

#         # Append cleaned description
#         fixed_row.append(reconstructed_description)

#         # Now append environment and duedate
#         if i + 1 < len(row):
#             fixed_row.append(row[i + 1])  # environment
#         else:
#             fixed_row.append('')  # fill if missing

#         if i + 2 < len(row):
#             fixed_row.append(row[i + 2])  # duedate
#         else:
#             fixed_row.append('')  # fill if missing

#         # Then the rest of the row starting from i + 3
#         fixed_row.extend(row[i + 3:])

#         writer.writerow(fixed_row)


# Filter out resolved issues that were not actually resolved
with open('csv_files/4-issues_recent_cleaned.csv', mode='r', encoding='utf-8', newline='') as infile, \
     open('csv_files/4.1-issues_recent_resolved.csv', mode='w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader((line.replace('\x00', '') for line in infile))
    writer = csv.writer(outfile)

    header = next(reader)
    writer.writerow(header)

    for row in reader:
        if len(row) > 24:
            status = row[14].strip()

            if status == "'Fixed'":
                try:
                    timespent = int(row[24].strip()) # disregard issues that have no time spent
                    if timespent != 0:
                        writer.writerow(row)
                except ValueError:
                    continue  


# Dictionary to group rows by NAME (e.g., AAR, ACCUMULO)
groups = defaultdict(list)

with open('csv_files/4.1-issues_recent_resolved.csv', mode='r', encoding='utf-8', newline='') as infile:
    reader = csv.reader((line.replace('\x00', '') for line in infile))
    header = next(reader)

    for row in reader:
        key = row[1].strip()  # index 1 is the 'key'
        if '-' in key:
            prefix = key.split('-')[0]
            groups[prefix].append(row)


# Sample 2 per group (if at least 2 exist), or all if fewer
sampled_rows = []
for group_rows in groups.values():
    if len(group_rows) <= 2:
        sampled_rows.extend(group_rows)
    else:
        sampled_rows.extend(random.sample(group_rows, 2))


# Write intermediate sample to a temp file
intermediate_file = 'csv_files/4.2-issues_sample_wip.csv'
with open(intermediate_file, mode='w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)
    writer.writerows(sampled_rows)


# Reopen and sample exactly 385 rows
final_sample_file = 'csv_files/5-issues_sample.csv'
with open(intermediate_file, mode='r', encoding='utf-8', newline='') as infile:
    reader = list(csv.reader(infile))
    header = reader[0]
    data_rows = reader[1:]

    if len(data_rows) < 385:
        raise ValueError(f"Not enough rows to sample 385. Only {len(data_rows)} available.")

    final_sample = random.sample(data_rows, 385)


# Write final sample
with open(final_sample_file, mode='w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)
    writer.writerows(final_sample)