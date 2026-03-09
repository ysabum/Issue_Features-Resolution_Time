'''
Script to turn .sql dump files into CSV format
'''

#!/usr/bin/env python
import fileinput
import csv
import sys
import os
from langdetect import detect, LangDetectException
import re
import random
from collections import defaultdict
from datetime import datetime

# This prevents prematurely closed pipes from raising
# an exception in Python
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

# allow large content in the dump
csv.field_size_limit(sys.maxsize)

def is_insert(line):
    """
    Returns true if the line begins a SQL insert statement.
    """
    return line.startswith('INSERT INTO')


def get_values(line):
    """
    Returns the portion of an INSERT statement containing values
    """
    return line.partition(' VALUES ')[2]


def values_sanity_check(values):
    """
    Ensures that values from the INSERT statement meet basic checks.
    """
    assert values
    assert values[0] == '('
    # Assertions have not been raised
    return True


def parse_values(values, outfile):
    """
    Given a file handle and the raw values from a MySQL INSERT
    statement, write the equivalent CSV to the file
    """
    latest_row = []

    # Specify the escapechar in the csv.writer initialization
    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
    
    reader = csv.reader([values], delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar="'",
                        strict=True
    )

    for reader_row in reader:
        for column in reader_row:
            # If our current string is empty...
            if len(column) == 0 or column == 'NULL':
                latest_row.append(chr(0))
                continue
            # If our string starts with an open paren
            if column[0] == "(":
                # If we've been filling out a row
                if len(latest_row) > 0:
                    # Check if the previous entry ended in
                    # a close paren. If so, the row we've
                    # been filling out has been COMPLETED
                    # as:
                    #    1) the previous entry ended in a )
                    #    2) the current entry starts with a (
                    if latest_row[-1][-1] == ")":
                        # Remove the close paren.
                        latest_row[-1] = latest_row[-1][:-1]
                        writer.writerow(latest_row)
                        latest_row = []
                # If we're beginning a new row, eliminate the
                # opening parentheses.
                if len(latest_row) == 0:
                    column = column[1:]
            # Add our column to the row we're working on.
            latest_row.append(column)
        # At the end of an INSERT statement, we'll
        # have the semicolon.
        # Make sure to remove the semicolon and
        # the close paren.
        if latest_row[-1][-2:] == ");":
            latest_row[-1] = latest_row[-1][:-2]
            writer.writerow(latest_row)


def main():
    """
    Parse arguments and start the program
    """
    # Define the output CSV file path
    output_file = 'csv_files/issues.csv'

    try:
        # Open the CSV file for writing
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            # Iterate over all lines in all files
            # listed in sys.argv[1:]
            # or stdin if no args given.
            for line in fileinput.input():
                # Look for an INSERT statement and parse it.
                if not is_insert(line):
                    raise Exception("SQL INSERT statement could not be found!")
                values = get_values(line)
                if not values_sanity_check(values):
                    raise Exception("Getting substring of SQL INSERT statement after ' VALUES ' failed!")
                parse_values(values, outfile)
    except KeyboardInterrupt:
        sys.exit(0)


    '''
    Script to narrow down issues to those that have been resolved in the recent past and have English language summary.
    '''


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



if __name__ == "__main__":
    main()