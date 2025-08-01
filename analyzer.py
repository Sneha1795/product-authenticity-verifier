import re
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.util import ngrams
from rapidfuzz import fuzz, process
nltk.download('punkt', quiet=True)

# Common suspicious phrases that could indicate fake products
RED_FLAG_KEYWORDS = [
    "replica", "copy", "fake", "authentic?", "genuine?", "looks like", "not original", "1st copy",
    "dupe", "knockoff", "mirror of", "inspired by", "just like original", "top copy", "same as original", "clone version",
    "mirror copy", "mirror version", "master copy", "duplicate"
]

# Valid spec keys for most tech products
KNOWN_KEYS = ['storage', 'camera', 'brand', 'price', 'battery', 'bluetooth', 'color', 'size', 'power', 'port']

ps = PorterStemmer()

# Try to fix misspelled spec keys using fuzzy matching
def normalize_keys(specs):
    corrected = {}
    warnings = []
    for key, value in specs.items():
        key_lower = key.lower().strip()
        best_match, score, _ = process.extractOne(key_lower, KNOWN_KEYS)
        if score >= 80:
            corrected[best_match] = value
        else:
            corrected[key_lower] = value
            warnings.append((f"Unknown spec key: '{key}'", "warning"))
    return corrected, warnings

# Clean up and simplify input text
def normalize_text(text):
    return text.lower().strip()

# Remove units (like GB/MP/MAh) for easier comparisons
def normalize_spec_value(val):
    return normalize_text(val).replace(" ", "").replace("gb", "").replace("mp", "").replace("mah", "")

# Check if the text contains suspicious keywords or phrasing
def contains_red_flags(text):
    flags = []
    text = normalize_text(text)
    tokens = word_tokenize(text)
    stems = [ps.stem(t) for t in tokens]
    bigrams = [' '.join(b) for b in ngrams(tokens, 2)]

    for keyword in RED_FLAG_KEYWORDS:
        keyword_lower = keyword.lower()
        keyword_tokens = word_tokenize(keyword_lower)
        keyword_stems = [ps.stem(t) for t in keyword_tokens]

        # Exact keyword match
        if keyword_lower in text:
            flags.append((keyword, "minor"))
            continue

        # Two word pattern match 
        if keyword_lower in bigrams:
            flags.append((f"[bigram match: {keyword}]", "minor"))
            continue

        # Similar words (typos or variations)
        for word in tokens:
            if fuzz.partial_ratio(word, keyword) >= 85:
                flags.append((f"[fuzzy match: {keyword}]", "minor"))
                break
        else:
            # If stems match (e.g., "copi" matches "copy", "copied")
            if all(k_stem in stems for k_stem in keyword_stems):
                flags.append((f"[stem match: {keyword}]", "minor"))

    return flags

# Look for suspicious or incorrect specs based on the product description
def check_spec_mismatches(specs, description=""):
    mismatches = []
    desc = normalize_text(description)

    brand = normalize_text(specs.get('brand', ''))
    price = specs.get('price', '')
    storage = normalize_text(specs.get('storage', ''))

    if brand in ['unknown', 'na', 'not mentioned', '']:
        mismatches.append(("Brand not specified", "critical"))

    if price:
        try:
            price_value = float(price)
            if price_value < 100:
                mismatches.append(("Price suspiciously low", "critical"))
        except:
            mismatches.append(("Price not numeric", "warning"))

    # If description says 128GB but spec shows 64, flag it
    if "128gb" in desc and "64" in storage:
        mismatches.append(("Storage mismatch with description", "warning"))

    if storage:
        try:
            storage_num = int("".join([c for c in storage if c.isdigit()]))
            if storage_num > 512:
                mismatches.append(("Storage value unusually high", "warning"))
        except:
            mismatches.append(("Storage format invalid", "warning"))

    return mismatches

# Review analysis: catch repeated reviews or sketchy phrases
def analyze_reviews(reviews):
    red_flags = []
    repeated_lines = set()
    seen = set()

    for review in reviews:
        review = review.strip()
        if review in seen:
            repeated_lines.add(review)
        seen.add(review)
        red_flags.extend(contains_red_flags(review))

    repeated = [(f"Repeated review: {r}", "warning") for r in repeated_lines]
    return repeated, red_flags

# Main analysis function
def analyze_product(data):
    raw_specs = data.get("specs", {})
    specs, unknown_key_warnings = normalize_keys(raw_specs)

    description = data.get("description", "")
    reviews = data.get("reviews", [])

    spec_flags = check_spec_mismatches(specs, description)
    repeated_reviews, review_flags = analyze_reviews(reviews)

    all_issues = spec_flags + repeated_reviews + review_flags + unknown_key_warnings

    # Scoring: remove points based on how serious the issues are
    score = 100
    for _, severity in all_issues:
        if severity == "critical":
            score -= 15
        elif severity == "warning":
            score -= 10
        elif severity == "minor":
            score -= 5
    score = max(0, min(100, score))

    # Format issue messages nicely
    explanations = []
    for message, severity in all_issues:
        prefix = "❌" if severity == "critical" else "⚠️" if severity == "warning" else "🟡"
        explanations.append(f"{prefix} {message} ({severity.capitalize()})")

    return {
        "confidence_score": score,
        "explanations": explanations
    }




