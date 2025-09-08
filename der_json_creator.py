import streamlit as st
import json
import re
import io

# -------------------------------
# Function to clean SQL queries
# -------------------------------
def clean_sql_query(file):
    """Remove comments from SQL and convert query into a single line."""
    content = file.read().decode("utf-8")

    # Remove block comments (/* ... */)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

    # Remove single-line comments (-- ...)
    content = re.sub(r"--.*?$", "", content, flags=re.MULTILINE)

    # Convert into single line
    return re.sub(r"\s+", " ", content).strip()


# -------------------------------
# Function to create final JSON
# -------------------------------
def create_final_json(uploaded_files):
    """Create a fresh JSON from scratch with cleaned queries."""
    metrics = []

    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        cleaned_query = clean_sql_query(uploaded_file)

        metric_block = {
            "id": idx,
            "metric": f"DER_{275 + idx - 1}",  # Dynamic metric name if needed
            "level": "l2",
            "supported_customers": {
                "included": [],
                "excluded": [
                    "kaiser-staging",
                    "kpphm-prod",
                    "kpphmi-prod",
                    "kpphmi-staging",
                    "kpwa-prod",
                    "kpwa-staging",
                    "jhah-prod"
                ]
            },
            "queries": {
                "snowflake": {
                    "database": "DAP",
                    "schema": "L2",
                    "query": cleaned_query
                },
                "postgres": {
                    "database": "postgres",
                    "schema": "l2",
                    "query": cleaned_query
                }
            }
        }

        metrics.append(metric_block)

    # Final JSON structure
    final_json = {"metrics": metrics}
    return final_json


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="DER JSON CREATOR", layout="wide")
st.title("📌 DER JSON CREATOR")

st.write("### Upload one or multiple `.sql` files to generate a clean JSON:")

# File uploader
uploaded_files = st.file_uploader(
    "Upload your SQL files",
    type=["sql"],
    accept_multiple_files=True
)

if uploaded_files:
    # Create final JSON
    final_json = create_final_json(uploaded_files)

    # Convert JSON to bytes for download
    json_bytes = io.BytesIO()
    json_bytes.write(json.dumps(final_json, indent=4).encode("utf-8"))
    json_bytes.seek(0)

    # Show preview
    st.write("### 🔍 JSON Preview")
    st.json(final_json)

    # Download button
    st.download_button(
        label="⬇️ Download JSON",
        data=json_bytes,
        file_name="DER_JSON_FINAL.json",
        mime="application/json"
    )
