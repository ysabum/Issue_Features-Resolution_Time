import os
import csv
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Load API Key
dotenv_path = BASE_DIR / "apiKey" / "api_key.env"
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

csv.field_size_limit(sys.maxsize)
MAX_CHARS = 6000

input_path = BASE_DIR / "csvIntermediate" / "4.1-issues_recent_resolved.csv"
output_path = BASE_DIR / "csvIntermediate" / "6-issues_analyzed.csv"

group_counts = {}
MAX_PER_GROUP = 6

# Resume logic: count existing rows
existing_rows = 0
if output_path.exists():
    with open(output_path, mode='r', encoding='utf-8', newline='') as f:
        existing_rows = sum(1 for _ in f) - 1  # subtract header

# Open files
with open(input_path, mode='r', encoding='utf-8', newline='') as infile, \
     open(output_path, mode='a', encoding='utf-8', newline='') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Skip header of input
    next(reader)

    # If file is empty, write header
    if existing_rows < 0:
        writer.writerow([
            'id', 'key', 'self', 'resolutiondate', 'created',
            'resolutiontime', 'timespent', 'titlelength', 'commentlength',
            'tone', 'tone_keywords',
            'relevance', 'relevant_keywords'
        ])

    # Skip already processed rows in input
    for _ in range(existing_rows + 1):
        next(reader)

    # Process remaining rows
    for row in reader:
        if len(row) > 24 and row[9].strip():

            key = row[1]
            group = key.split("-")[0]

            # Limit to 6 issues per group
            count = group_counts.get(group, 0)
            if count >= MAX_PER_GROUP:
                continue

            group_counts[group] = count + 1

            summary = row[8].strip()
            description = row[9].strip()
            comment_length = len(description)

            resolution_date_str = row[4].strip().strip('"').strip("'")
            created_date_str = row[5].strip().strip('"').strip("'")
            timespent = int(row[24].strip())

            # Truncate long text if needed
            text = f"{summary}\n\n{description}"
            if len(text) > MAX_CHARS:
                description = description[:MAX_CHARS - len(summary)]

            prompt = f"""
Given the following:

Summary: {summary}
Description: {description}

Tasks:
1. Determine the tone of the description (choose one: professional, frustrated, neutral, urgent, casual, angry, unclear).
2. Determine if the description is relevant to the summary (Yes/No).
3. If relevant, extract the key words or phrases in the description that make it relevant to the summary.
4. If the tone is NOT professional or neutral, extract the words/phrases that justify the tone.

Respond ONLY in JSON format:

{{
  "tone": "neutral",
  "tone_keywords": "",
  "relevant": "Yes",
  "relevant_keywords": "login fails, invalid credentials"
}}
"""

            try:
                resolution_date = datetime.strptime(resolution_date_str[:19], '%Y-%m-%dT%H:%M:%S')
                created_date = datetime.strptime(created_date_str[:19], '%Y-%m-%dT%H:%M:%S')
                resolution_time = (resolution_date - created_date).days

                title_length = len(summary)

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing software issue reports."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                content = response.choices[0].message.content.strip()

                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    content = content[content.find("{"):content.rfind("}")+1]
                    result = json.loads(content)

                tone = result.get('tone', '')
                tone_keywords = result.get('tone_keywords', '')
                relevance_flag = result.get('relevant', '').lower()
                relevant_keywords = result.get('relevant_keywords', '')

                relevance = 1 if relevance_flag == 'yes' else 0

                writer.writerow([
                    row[0], row[1], row[2],
                    row[4], row[5],
                    resolution_time,
                    row[24],
                    title_length,
                    comment_length,
                    tone,
                    tone_keywords,
                    relevance,
                    relevant_keywords
                ])

            except Exception as e:
                print(f"Error analyzing row: {e}")
                continue



















'''
Old code; rewrites entire csv. 
'''
# import os
# import csv
# import sys
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
# from datetime import datetime
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent

# # Load API Key
# dotenv_path = BASE_DIR / "apiKey" / "api_key.env"
# load_dotenv(dotenv_path)

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

# csv.field_size_limit(sys.maxsize)
# MAX_CHARS = 6000

# input_path = BASE_DIR / "csvIntermediate" / "4.1-issues_recent_resolved.csv"
# output_path = BASE_DIR / "csvIntermediate" / "6-issues_analyzed.csv"

# # Track counts per group (e.g., ACCUMULO, ARROW, HADOOP)
# group_counts = {}
# MAX_PER_GROUP = 6

# with open(input_path, mode='r', encoding='utf-8', newline='') as infile, \
#      open(output_path, mode='w', encoding='utf-8', newline='') as outfile:

#     reader = csv.reader(infile)
#     writer = csv.writer(outfile)

#     # Skip header of input
#     next(reader)

#     # Always write header for output
#     writer.writerow([
#         'id', 'key', 'self', 'resolutiondate', 'created',
#         'resolutiontime', 'timespent', 'titlelength', 'commentlength',
#         'tone', 'tone_keywords',
#         'relevance', 'relevant_keywords'
#     ])

#     for row in reader:
#         # Must have description and enough columns
#         if len(row) > 24 and row[9].strip():

#             key = row[1]
#             group = key.split("-")[0]

#             # Limit to 6 issues per group
#             count = group_counts.get(group, 0)
#             if count >= MAX_PER_GROUP:
#                 continue

#             group_counts[group] = count + 1

#             summary = row[8].strip()
#             description = row[9].strip()
#             comment_length = len(description)

#             resolution_date_str = row[4].strip().strip('"').strip("'")
#             created_date_str = row[5].strip().strip('"').strip("'")
#             timespent = int(row[24].strip())

#             # Truncate long text if needed
#             text = f"{summary}\n\n{description}"
#             if len(text) > MAX_CHARS:
#                 description = description[:MAX_CHARS - len(summary)]

#             prompt = f"""
# Given the following:

# Summary: {summary}
# Description: {description}

# Tasks:
# 1. Determine the tone of the description (choose one: professional, frustrated, neutral, urgent, casual, angry, unclear).
# 2. Determine if the description is relevant to the summary (Yes/No).
# 3. If relevant, extract the key words or phrases in the description that make it relevant to the summary.
# 4. If the tone is NOT professional or neutral, extract the words/phrases that justify the tone.

# Respond ONLY in JSON format:

# {{
#   "tone": "neutral",
#   "tone_keywords": "",
#   "relevant": "Yes",
#   "relevant_keywords": "login fails, invalid credentials"
# }}
# """

#             try:
#                 resolution_date = datetime.strptime(resolution_date_str[:19], '%Y-%m-%dT%H:%M:%S')
#                 created_date = datetime.strptime(created_date_str[:19], '%Y-%m-%dT%H:%M:%S')
#                 resolution_time = (resolution_date - created_date).days

#                 title_length = len(summary)

#                 response = client.chat.completions.create(
#                     model="gpt-3.5-turbo",
#                     messages=[
#                         {"role": "system", "content": "You are an expert in analyzing software issue reports."},
#                         {"role": "user", "content": prompt}
#                     ],
#                     temperature=0.3
#                 )

#                 content = response.choices[0].message.content.strip()

#                 try:
#                     result = json.loads(content)
#                 except json.JSONDecodeError:
#                     content = content[content.find("{"):content.rfind("}")+1]
#                     result = json.loads(content)

#                 tone = result.get('tone', '')
#                 tone_keywords = result.get('tone_keywords', '')
#                 relevance_flag = result.get('relevant', '').lower()
#                 relevant_keywords = result.get('relevant_keywords', '')

#                 relevance = 1 if relevance_flag == 'yes' else 0

#                 writer.writerow([
#                     row[0], row[1], row[2],
#                     row[4], row[5],
#                     resolution_time,
#                     row[24],
#                     title_length,
#                     comment_length,
#                     tone,
#                     tone_keywords,
#                     relevance,
#                     relevant_keywords
#                 ])

#             except Exception as e:
#                 print(f"Error analyzing row: {e}")
#                 continue