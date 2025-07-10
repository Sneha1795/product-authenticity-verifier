import pandas as pd
import nltk
import re
from nltk.corpus import stopwords

# Download stopwords (once only)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Config
RED_FLAG_KEYWORDS = ['first copy', 'fake', 'replica', 'used', 'cheap original', 'not original', 'clone']
SPEC_KEYWORDS = ['512gb', '256gb', '128gb']
STOPWORDS = set(stopwords.words('english'))
REVIEW_REPEAT_THRESHOLD = 2

# Sample product data (hardcoded for testing)
data = [
    {
        'product_id': 'B001',
        'title': 'iPhone 14 Pro',
        'description': 'Brand new iPhone 14 Pro, 512GB',
        'reviews': 'Not 512GB||Looks used||Battery was 80%'
    },
    {
        'product_id': 'B002',
        'title': 'Nike Air Max',
        'description': 'First copy of Nike shoes, original sole',
        'reviews': 'First copy||Looks original||Bit fake'
    },
    {
        'product_id': 'B003',
        'title': 'Sony Headphones',
        'description': 'New sealed Sony headphones, 128GB',
        'reviews': 'Great quality||Exactly what I expected'
    }
]

df = pd.DataFrame(data)

# Clean & tokenize text using regex (no punkt needed)
def clean_text(text):
    tokens = re.findall(r'\b\w+\b', str(text).lower())
    return [t for t in tokens if t not in STOPWORDS]

def detect_keywords(tokens, keyword_list):
    return [kw for kw in keyword_list if any(kw in token for token in tokens)]

def check_spec_mismatch(desc_tokens, reviews):
    desc_gb = next((gb for gb in SPEC_KEYWORDS if gb in desc_tokens), None)
    if not desc_gb:
        return None
    for r in reviews:
        if any(gb in r for gb in SPEC_KEYWORDS if gb != desc_gb):
            return f"Spec mismatch: desc has {desc_gb}, review mentions something else"
    return None

def detect_review_spam(reviews):
    cleaned = [r.strip().lower() for r in reviews]
    return "Review spam detected" if len(set(cleaned)) < len(cleaned) else None

def analyze_row(row):
    issues = []
    score = 0

    title_tokens = clean_text(row['title'])
    desc_tokens = clean_text(row['description'])
    reviews_raw = str(row['reviews']).split('||')
    review_tokens = [clean_text(r) for r in reviews_raw]
    flat_review_tokens = [token for sublist in review_tokens for token in sublist]

    # Combine all tokens
    combined_tokens = title_tokens + desc_tokens + flat_review_tokens

    # Red-flag keywords
    found_keywords = detect_keywords(combined_tokens, RED_FLAG_KEYWORDS)
    if found_keywords:
        issues.append(f"Red-flag keywords: {', '.join(found_keywords)}")
        score += len(found_keywords)

    # Spec mismatch
    spec_issue = check_spec_mismatch(desc_tokens, reviews_raw)
    if spec_issue:
        issues.append(spec_issue)
        score += 1

    # Review spam
    spam_issue = detect_review_spam(reviews_raw)
    if spam_issue:
        issues.append(spam_issue)
        score += 1

    return {
        'score': score,
        'confidence': round(score / 5, 2),
        'issues': issues
    } if issues else None

# Apply logic
df['analysis'] = df.apply(analyze_row, axis=1)

# Print output
for _, row in df.iterrows():
    print(f"\nProduct ID: {row['product_id']}")
    print(f"Title: {row['title']}")
    if row['analysis']:
        print("🔴 FLAGGED")
        for issue in row['analysis']['issues']:
            print(f" - {issue}")
        print(f"Confidence Score: {row['analysis']['confidence']}")
    else:
        print("✅ Looks clean")


