'''
Script to preprocess issue summaries and descriptions using NLP techniques.

Operations performed:
1. Lowercasing / normalization
2. Sentence segmentation
3. Punctuation removal
4. Word tokenization
5. Word count computation

The processed results are written to a new CSV file.
'''

import csv
import sys
import re
import string

csv.field_size_limit(sys.maxsize)

input_file = 'csv_files/5-issues_sample.csv'
output_file = 'csv_files/6-issues_nlp_processed.csv'


def preprocess_text(text):
    """Perform NLP preprocessing on text."""

    if text.strip() == '' or text.strip() == 'NULL':
        return "", [], [], 0, 0

    # Normalize text
    normalized_text = text.lower()

    # Sentence segmentation
    sentences = re.split(r'[.!?]+', normalized_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Remove punctuation
    cleaned_text = normalized_text.translate(str.maketrans('', '', string.punctuation))

    # Tokenization
    tokens = cleaned_text.split()

    # Word count
    word_count = len(tokens)

    # Sentence count
    sentence_count = len(sentences)

    return normalized_text, tokens, sentences, word_count, sentence_count


with open(input_file, mode='r', encoding='utf-8', newline='') as infile, \
     open(output_file, mode='w', encoding='utf-8', newline='') as outfile:

    reader = csv.reader((line.replace('\x00', '') for line in infile))
    writer = csv.writer(outfile)

    header = next(reader)

    # Add new NLP columns
    new_header = header + [
        "summary_word_count",
        "description_word_count",
        "summary_sentence_count",
        "description_sentence_count"
    ]

    writer.writerow(new_header)

    for row in reader:

        if len(row) > 9:
            summary = row[8].strip()
            description = row[9].strip()

            # Process summary
            s_norm, s_tokens, s_sentences, s_word_count, s_sentence_count = preprocess_text(summary)

            # Process description
            d_norm, d_tokens, d_sentences, d_word_count, d_sentence_count = preprocess_text(description)

            writer.writerow(row + [
                s_word_count,
                d_word_count,
                s_sentence_count,
                d_sentence_count
            ])