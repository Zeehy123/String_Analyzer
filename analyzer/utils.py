import hashlib
from collections import Counter


def compute_component(value:str)->dict:

  length=len(value)
  is_palindrome=value.lower()==value.lower()[::-1]
  unique_characters=len(set(value))
  word_count=len(value.split())
  sha256_hash=hashlib.sha256(value.encode("utf-8")).hexdigest()
  frequency=dict(Counter(value))

  return{
    "length":length,
    "is_palindrome":is_palindrome,
    "unique_characters":unique_characters,
    "word_count":word_count,
    "sha256_hash":sha256_hash,
    "character_frequency":frequency
  }


from decimal import Decimal

def make_json_safe(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    else:
        return obj


import re


import re

def parse_nl_query(query: str) -> dict:
    """
    Parses a natural language query and returns a dictionary
    with filter keys matching the filter names in StringAnalysisResultFilter.
    """
    query = query.lower().strip()
    filters = {}

    # Word count filters
    if "single word" in query or "one word" in query:
        filters["word_count"] = 1
    elif "two words" in query:
        filters["word_count"] = 2
    elif "three words" in query:
        filters["word_count"] = 3

    # Palindrome
    if "palindrom" in query:  # matches 'palindrome' or 'palindromic'
        filters["is_palindrome"] = True

    # Length comparisons
    length_match = re.search(r"length (greater|less|equal) to (\d+)", query)
    if length_match:
        operator = length_match.group(1)
        length_threshold = int(length_match.group(2))
        if operator == "greater":
            filters["min_length"] = length_threshold + 1
        elif operator == "less":
            filters["max_length"] = length_threshold - 1
        elif operator == "equal":
            filters["min_length"] = filters["max_length"] = length_threshold

    # Between X and Y
    between_match = re.search(r"between (\d+) and (\d+)", query)
    if between_match:
        filters["min_length"] = int(between_match.group(1))
        filters["max_length"] = int(between_match.group(2))

    # Contains character
    contain_letter = re.search(r"(?:contain(?:ing|s)?(?: the)? letter )([a-z])", query)
    if contain_letter:
        filters["contains_character"] = contain_letter.group(1)

    if not filters:
        raise ValueError("No valid filters found in the query.")

    return filters
