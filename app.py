import streamlit as st
from analyzer import analyze_product  # Import the main analysis function

# Page Configuration
st.set_page_config(page_title="Product Authenticity Verifier", layout="centered")

# App Header
st.title(" Product Authenticity Verifier")
st.write("Enter product information to check for suspicious or fake listing patterns.")

# User Inputs: Title and Description
title = st.text_input(" Product Title")  # Product name
description = st.text_area(" Product Description", height=150)  # Full product description

# User Input: Key-Value Specs
st.subheader(" Product Specs (key: value format)")
spec_input = st.text_area("Example:\nStorage: 128GB\nCamera: 12MP\nBrand: Sony", height=100)

# User Input: Customer Reviews
st.subheader(" Product Reviews")
reviews_input = st.text_area("Enter one review per line", height=150)

# Analyze Button
if st.button("🔍 Analyze Product"):
    if not title or not description:
        # Basic validation check for required fields
        st.warning("Please enter both a title and a description.")
    else:
        # Process Specs
        specs = {}
        for line in spec_input.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                specs[key.strip().lower()] = value.strip()

        # Process Reviews
        reviews = [r.strip() for r in reviews_input.strip().split("\n") if r.strip()]

        # Build Product Dictionary
        product = {
            "product_id": "user_input",  # ID is dummy since input is manual
            "title": title,
            "description": description,
            "specs": specs,
            "reviews": reviews
        }

        # Run Analysis
        result = analyze_product(product)

        # Show Result to User
        st.subheader("🔍 Analysis Result")
        if result['explanations']:
            # Show warning if issues were found
            st.error("⚠️ Suspicious Listing Detected!")
            st.markdown(f"**Confidence Score:** `{result['confidence_score']}/100`")
            st.markdown("**Issues by Severity:**")
            for explanation in result['explanations']:
                st.write(f"- {explanation}")
        else:
            # Show success message if product seems genuine
            st.success("✅ No issues detected. This product seems genuine.")
            st.markdown(f"**Confidence Score:** `{result['confidence_score']}/100`")




