import os
import csv
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Load API Key
dotenv_path = BASE_DIR / "apiKey" / "api_key.env"
load_dotenv(dotenv_path)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

csv.field_size_limit(sys.maxsize)

input_path = BASE_DIR / "csvIntermediate" / "crdft.csv"
output_path = BASE_DIR / "csvIntermediate" / "toxic-keywords.csv"

with open(input_path, mode='r', encoding='utf-8', newline='') as infile, \
     open(output_path, mode='w', encoding='utf-8', newline='') as outfile:

    reader = csv.DictReader(infile)

    # FIX BOM in header
    reader.fieldnames = [name.lstrip("\ufeff") for name in reader.fieldnames]

    writer = csv.writer(outfile)
    writer.writerow([
        "message", "created", "resolutiondate", "resolutiontime",
        "commentlength", "toxic_keywords"
    ])

    for row in reader:
        message = row["message"].strip()
        is_toxic = row["is_toxic"].strip()
        created = row["created"].strip()
        resolutiondate = row["resolutiondate"].strip()
        resolutiontime = row["resolutiontime"].strip()

        commentlength = len(message)

        # If not toxic, skip OpenAI call
        if is_toxic == "0":
            writer.writerow([
                message, created, resolutiondate, resolutiontime,
                commentlength, ""
            ])
            continue

        prompt = f"""
Message: {message}

Task:
Identify the specific words or short phrases in the message that make it toxic.
Return ONLY JSON in this format:

{{
  "toxic_keywords": "..."
}}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You extract toxic keywords from text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            content = response.choices[0].message.content.strip()

            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                content = content[content.find("{"):content.rfind("}")+1]
                result = json.loads(content)

            toxic_keywords = result.get("toxic_keywords", "")

            writer.writerow([
                message, created, resolutiondate, resolutiontime,
                commentlength, toxic_keywords
            ])

        except Exception as e:
            print(f"Error analyzing row: {e}")
            writer.writerow([
                message, created, resolutiondate, resolutiontime,
                commentlength, ""
            ])
            continue