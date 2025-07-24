# product-authenticity-verifier

A **rule-based NLP tool** to detect potentially fake or misleading e-commerce product listings by analyzing product descriptions, specifications, and reviews.

## Features
- Scans product descriptions and reviews for red-flag keywords like "replica", "copy", "fake", etc.
- Checks for spec mismatches (e.g., storage value in description vs. specs, suspiciously low prices).
- Flags repeated reviews as suspicious.
- Assigns a confidence score (0–100) based on the severity of detected issues.
- Provides detailed explanations for each detected issue.
- Supports batch analysis of multiple products using `test_data.json` and generates `analysis_report.csv`.
- Includes a Streamlit-based web app for analyzing single products interactively.

## Tools & Libraries
- **Python**
- **Pandas** – For handling product data and batch analysis.
- **NLTK** – For basic text tokenization.
- **Regex** – For pattern matching in descriptions and reviews.
- **NumPy** – For basic computations.
- **RapidFuzz** – For fuzzy matching of spec keys.
- **Streamlit** – For building the web app interface.

## Project Files
- **analyzer.py** – Core logic for analyzing a single product (keywords, specs, reviews, and scoring).
- **app.py** – Streamlit web app for interactive product analysis.
- **batchanalysis.py** – Batch analysis script for processing `test_data.json` and generating a report.
- **test_data.json** – Sample product listing data for testing batch analysis.
- **requirements.txt** – Python dependencies.
- **.gitignore** – Ignores cache files, temporary files, and CSV outputs.

## How to run
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
3. `python batchanalysis.py`
