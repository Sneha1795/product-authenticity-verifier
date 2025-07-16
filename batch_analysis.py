# batch_analysis.py

"""
Batch analyzer for Product Authenticity Verifier.

Loads 'test_data.json' (a list of product listings),
runs analysis from analyzer.py on each product,
and saves results to 'analysis_report.csv'.
"""

import pandas as pd
import json
from analyzer import analyze_product

# --- Load test data from test_data.json ---
with open("test_data.json", "r") as file:
    products = json.load(file)

# --- Convert list of product dicts into a DataFrame ---
df = pd.DataFrame(products)

# --- Analyze each product using your existing logic ---
df["analysis_result"] = df.apply(lambda row: analyze_product(row), axis=1)

# --- Extract analysis details into new columns ---
df["confidence_score"] = df["analysis_result"].apply(lambda r: r["confidence_score"])
df["num_spec_issues"] = df["analysis_result"].apply(lambda r: len(r["spec_issues"]))
df["num_review_issues"] = df["analysis_result"].apply(lambda r: len(r["repeated_reviews"]))
df["num_red_flags"] = df["analysis_result"].apply(lambda r: len(r["red_flag_keywords"]))
df["total_issues"] = df["num_spec_issues"] + df["num_review_issues"] + df["num_red_flags"]

# --- Optional: Expand issue details (for debugging or CSV clarity) ---
df["spec_issues"] = df["analysis_result"].apply(lambda r: ", ".join(r["spec_issues"]))
df["repeated_reviews"] = df["analysis_result"].apply(lambda r: ", ".join(r["repeated_reviews"]))
df["red_flag_keywords"] = df["analysis_result"].apply(lambda r: ", ".join(r["red_flag_keywords"]))

# --- Save final report to CSV ---
df.to_csv("analysis_report.csv", index=False)

# --- Print summary to console ---
print("\n📊 Batch Analysis Summary:")
print(df[["product_id", "title", "confidence_score", "total_issues"]])

print("\n✅ Full report saved as 'analysis_report.csv'")

