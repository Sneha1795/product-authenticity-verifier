import streamlit as st
from analyzer import analyze_product

st.set_page_config(page_title="Product Authenticity Verifier", layout="centered")

st.title("🛡️ Product Authenticity Verifier")
st.write("Enter product information to check for suspicious or fake listing patterns.")

# --- Product Inputs ---
title = st.text_input("📦 Product Title")
description = st.text_area("📝 Product Description", height=150)

st.subheader("⚙️ Product Specs (key: value format)")
spec_input = st.text_area("Example:\nStorage: 128GB\nCamera: 12MP\nBrand: Sony", height=100)

st.subheader("⭐ Product Reviews")
reviews_input = st.text_area("Enter one review per line", height=150)

# --- Analyze Button ---
if st.button("🔍 Analyze Product"):
    if not title or not description:
        st.warning("Please enter both a title and a description.")
    else:
        # Convert specs
        specs = {}
        for line in spec_input.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                specs[key.strip().lower()] = value.strip()

        # Convert reviews
        reviews = [r.strip() for r in reviews_input.strip().split("\n") if r.strip()]

        product = {
            "product_id": "user_input",
            "title": title,
            "description": description,
            "specs": specs,
            "reviews": reviews
        }

        result = analyze_product(product)

        # --- Output ---
        st.subheader("🔍 Analysis Result")
        if result['explanations']:
            st.error("⚠️ Suspicious Listing Detected!")
            st.markdown(f"**Confidence Score:** `{result['confidence_score']}/100`")
            st.markdown("**Issues by Severity:**")
            for explanation in result['explanations']:
                st.write(f"- {explanation}")
        else:
            st.success("✅ No issues detected. This product seems genuine.")
            st.markdown(f"**Confidence Score:** `{result['confidence_score']}/100`")



