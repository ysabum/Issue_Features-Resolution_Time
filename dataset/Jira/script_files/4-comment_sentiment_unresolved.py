import openai
import os
import csv
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

dotenv_path = r'api_key/api_key.env'
load_dotenv(dotenv_path=dotenv_path)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI()

csv.field_size_limit(sys.maxsize)

# Define max tokens for input text
MAX_CHARS = 6000

with open('csv_files/`5-issues_sample_unresolved.csv', mode='r', encoding='utf-8', newline='') as infile, \
     open('csv_files/`6-issues_analyzed_unresolved.csv', mode='w', encoding='utf-8', newline='') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write new header with selected fields
    writer.writerow(['id', 'key', 'self', 'resolutiondate', 'created', 'commentlength', 'tone', 'relevance', 'descriptive'])

    next(reader)  # Skip header row

    for row in reader:
        if len(row) > 24 and row[9].strip():
            summary = row[8].strip()
            description = row[9].strip()

            # Truncate if too long
            text = f"{summary}\n\n{description}"
            if len(text) > MAX_CHARS:
                description = description[:MAX_CHARS - len(summary)]

            prompt = f"""
Given the following:
Summary: {summary}
Description: {description}

1. What is the tone of the description? (choose one: professional, frustrated, neutral, urgent, casual, angry, unclear)
2. Is the description relevant to the summary? (Yes/No)
3. Is the description descriptive and informative? (Yes/No)

Respond in JSON like this:
{{
"tone": "neutral",
"relevant": "Yes",
"descriptive": "Yes"
}}
"""

            try:
                comment_length = len(description)

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing customer support tickets."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                content = response.choices[0].message.content
                result = json.loads(content)

                tone = result.get('tone', '')
                relevance = 1 if result.get('relevant', '').lower() == 'yes' else 0
                descriptive = 1 if result.get('descriptive', '').lower() == 'yes' else 0

                writer.writerow([
                    row[0],  # id
                    row[1],  # key
                    row[2],  # self
                    row[4],  # resolutiondate
                    row[5],  # created
                    comment_length,
                    tone,
                    relevance,
                    descriptive
                ])

            except Exception as e:
                print(f"Error analyzing row: {e}")
                continue