import re
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from rapidfuzz import fuzz, process

nltk.download('punkt', quiet=True)

# --- Keyword Rules ---
RED_FLAG_KEYWORDS = [
    "replica", "copy", "fake", "authentic?", "genuine?", "looks like", "not original", "1st copy",
    "dupe", "knockoff", "mirror of", "inspired by", "just like original", "top copy", "same as original", "clone version"
]

# --- Valid Spec Keys ---
KNOWN_KEYS = ['storage', 'camera', 'brand', 'price', 'battery', 'bluetooth', 'color', 'size', 'power', 'port']

# --- Normalize Spec Keys with Fuzzy Matching ---
def normalize_keys(specs):
    corrected = {}
    warnings = []
    for key, value in specs.items():
        key_lower = key.lower().strip()
        best_match, score, _ = process.extractOne(key_lower, KNOWN_KEYS)
        if score >= 80:
            corrected[best_match] = value
        else:
            corrected[key_lower] = value  # keep original
            warnings.append((f"Unknown spec key: '{key}'", "warning"))
    return corrected, warnings

# --- Normalize Helpers ---
def normalize_text(text):
    return text.lower().strip()

def normalize_spec_value(val):
    return normalize_text(val).replace(" ", "").replace("gb", "").replace("mp", "").replace("mah", "")

# --- Detect Red Flags ---
def contains_red_flags(text):
    flags = []
    text = text.lower()
    for keyword in RED_FLAG_KEYWORDS:
        if keyword in text:
            flags.append((keyword, "minor"))
        else:
            for word in word_tokenize(text):
                similarity = fuzz.partial_ratio(word.lower(), keyword.lower())
                if similarity >= 85:
                    flags.append((f"[fuzzy match: {keyword}]", "minor"))
                    break
    return flags

# --- Check Spec Issues ---
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

# --- Analyze Reviews ---
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

    return [(f"Repeated review: {r}", "warning") for r in repeated_lines], red_flags

# --- Final Main Analyzer ---
def analyze_product(data):
    raw_specs = data.get("specs", {})
    specs, unknown_key_warnings = normalize_keys(raw_specs)

    description = data.get("description", "")
    reviews = data.get("reviews", [])

    spec_flags = check_spec_mismatches(specs, description)
    repeated_reviews, review_flags = analyze_reviews(reviews)

    all_issues = spec_flags + repeated_reviews + review_flags + unknown_key_warnings

    score = 100
    for _, severity in all_issues:
        if severity == "critical":
            score -= 15
        elif severity == "warning":
            score -= 10
        elif severity == "minor":
            score -= 5

    score = max(0, min(100, score))

    explanations = []
    for message, severity in all_issues:
        prefix = "❌" if severity == "critical" else "⚠️" if severity == "warning" else "🟡"
        explanations.append(f"{prefix} {message} ({severity.capitalize()})")

    return {
        "confidence_score": score,
        "explanations": explanations
    }



