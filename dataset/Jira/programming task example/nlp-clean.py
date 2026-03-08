"""
NLP Preprocessing Module for Issue Tracking Analysis

Program preprocesses issue titles and comments from issue 
tracking systems. It performs standard NLP preprocessing 
operations including tokenization, punctuation removal, 
normalization, sentence segmentation, and word counting.

The processed data can be used later for regression modeling to predict issue
resolution time.
"""

import re
import string


def preprocess_text(text):
    """
    Preprocess text using NLP techniques.

    Steps performed:
    1. Sentence segmentation
    2. Lowercasing
    3. Punctuation removal
    4. Word tokenization
    5. Word counting

    Parameters:
        text (str): Input text (issue title or comment)

    Returns:
        dict: Processed results including tokens, sentences, and counts
    """

    # Input validation
    if not isinstance(text, str) or len(text.strip()) == 0:
        raise ValueError("Input must be a non-empty string.")

    # Normalize text (lowercase)
    normalized_text = text.lower()

    # Sentence segmentation
    sentences = re.split(r'[.!?]+', normalized_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Remove punctuation
    cleaned_text = normalized_text.translate(str.maketrans('', '', string.punctuation))

    # Word tokenization
    tokens = cleaned_text.split()

    # Word count
    word_count = len(tokens)

    # Sentence count
    sentence_count = len(sentences)

    return {
        "original_text": text,
        "normalized_text": normalized_text,
        "tokens": tokens,
        "sentences": sentences,
        "word_count": word_count,
        "sentence_count": sentence_count
    }


def display_results(results):
    """
    Display preprocessing results.
    """

    print("\n--- NLP Preprocessing Results ---")

    print("\nOriginal Text:")
    print(results["original_text"])

    print("\nNormalized Text:")
    print(results["normalized_text"])

    print("\nSentences:")
    for s in results["sentences"]:
        print("-", s)

    print("\nTokens:")
    print(results["tokens"])

    print("\nWord Count:", results["word_count"])
    print("Sentence Count:", results["sentence_count"])


def main():
    """
    Main program execution.
    """

    print("Issue Comment NLP Preprocessing Tool")

    user_input = input("\nEnter an issue comment or title: ")

    try:
        results = preprocess_text(user_input)
        display_results(results)

    except ValueError as e:
        print("\nERROR:", e)


if __name__ == "__main__":
    main()