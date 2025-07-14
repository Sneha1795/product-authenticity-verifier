import json
import re
from collections import Counter
import pandas as pd
import nltk

nltk.download('punkt')

RED_FLAG_KEYWORDS = [
    'almost original', 'like original', 'cheap quality', 'replica', 'fake', 'copy',
    'not genuine', 'look alike', 'highly recommended', 'best price', 'discount', '100% original'
]

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_spec_mismatch(product):
    """
    Check if specs mentioned in title/description mismatch with specs dict.
    Very basic example: look for numbers in title and compare with specs values.
    """
    issues = []

    title = product.get('title', '').lower()
    specs = product.get('specs', {})

    # Extracting numbers with units from title
    title_numbers = re.findall(r'(\d+\s?(gb|mp|inch|inch|mah|hours))', title)

    # Flatten to just numbers with units
    title_specs = [t[0].replace(' ', '') for t in title_numbers]

    for key, val in specs.items():
        val_str = str(val).lower().replace(' ', '')
        if val_str not in title_specs:
            # Spec value missing in title specs? Could be mismatch or missing mention
            if title_specs:
                issues.append(f"Spec mismatch for {key}: '{val}' not found in title")
    return issues

def check_red_flag_keywords(product):
    issues = []
    text = (product.get('title', '') + ' ' + product.get('description', '')).lower()

    for kw in RED_FLAG_KEYWORDS:
        if kw in text:
            issues.append(f"Red-flag keyword detected: '{kw}'")

    return issues

def check_review_patterns(product):
    issues = []
    reviews = product.get('reviews', [])

    # Count repeated reviews
    review_counts = Counter(reviews)
    repeated = [r for r, count in review_counts.items() if count > 1]

    if repeated:
        issues.append(f"Repeated reviews detected: {len(repeated)} repeated review(s)")

    return issues

def analyze_product(product):
    issues = []
    issues.extend(check_spec_mismatch(product))
    issues.extend(check_red_flag_keywords(product))
    issues.extend(check_review_patterns(product))

    return issues

def main(file_path):
    products = load_data(file_path)
    flagged_products = []

    for product in products:
        issues = analyze_product(product)
        if issues:
            flagged_products.append({
                'product_id': product.get('product_id', 'N/A'),
                'title': product.get('title', ''),
                'issues': issues
            })

    if flagged_products:
        print("\n Flagged Products:")
        for p in flagged_products:
            print(f"\nProduct ID: {p['product_id']}")
            print(f"Title: {p['title']}")
            for issue in p['issues']:
                print(f" - {issue}")
    else:
        print("No issues detected in any products.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python analyzer.py <test_data.json>")
        sys.exit(1)
    main(sys.argv[1])


