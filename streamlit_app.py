import streamlit as st
import json
import yaml
from dotenv import load_dotenv
from openai import OpenAI
import os
import pandas as pd

# Load environment & OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load prompt & validation rules
with open("prompts/generate_test_payload.txt") as f:
    prompt_template = f.read()

with open("rules/validation_rules.yaml") as f:
    validation_rules = yaml.safe_load(f)

# Streamlit page config
st.set_page_config(page_title="GenAI Loan Test Data Generator", layout="wide")
st.title("📦 GenAI Loan Test Data Generator")

# User input: test cases
test_cases_text = st.text_area(
    "✍️ Enter test cases (one per line):",
    "Test loan amount exceeds estimated value\nTest underage applicant\nTest missing co-applicant"
)

results = []

if st.button("🚀 Generate Test Data"):
    # --- Input Validation ---
    if not test_cases_text or len(test_cases_text.strip()) < 10:
        st.error("❌ Please enter at least 10 characters for your test cases.")
        st.stop()
    # --- End Input Validation ---

    test_cases = [{"description": line.strip()} for line in test_cases_text.strip().split("\n") if line.strip()]

    # Build strong prompt to force JSON output
    prompt = prompt_template \
        .replace("{{schema}}", "<schema omitted for brevity>") \
        .replace("{{rules}}", yaml.dump(validation_rules)) \
        .replace("{{test_cases}}", json.dumps({"test_cases": test_cases}, indent=2)) \
        + "\nRespond ONLY with a JSON array matching this format. No markdown, no explanation."

    with st.spinner("Calling OpenAI..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a test data generation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            raw_content = response.choices[0].message.content.strip() if response.choices else ""
        except Exception as e:
            st.error(f"❌ OpenAI API call failed: {str(e)}")
            st.stop()

    if not raw_content:
        st.error("❌ Empty response from OpenAI.")
        st.stop()

    # Remove Markdown code fences if present
    if raw_content.startswith("```json"):
        raw_json = raw_content[7:-3].strip()
    elif raw_content.startswith("```"):
        raw_json = raw_content[3:-3].strip()
    else:
        raw_json = raw_content

    # Parse JSON safely
    try:
        parsed = json.loads(raw_json)
        st.success("✅ Successfully parsed JSON!")
    except json.JSONDecodeError as e:
        st.error(f"❌ Could not parse JSON.\nError: {e}\nRaw content:\n{raw_json}")
        st.stop()

    # Store results
    results = [{
        "test_case": item["test_case"],
        "payload": item["payload"],
        "explanation": item.get("explanation", "")
    } for item in parsed]

    if results:
        st.markdown("## 🧪 Generated Test Cases")

        for idx, r in enumerate(results, start=1):
            with st.container():
                st.markdown(f"### {idx}. {r['test_case']}")
                st.write(f"**Explanation:** {r['explanation']}")
                st.write("**Payload:**")
                st.json(r["payload"])

        # Export all to CSV
        df = pd.DataFrame([{
            "Test Case": r["test_case"],
            "Test Data": json.dumps(r["payload"], indent=2),
            "Explanation": r["explanation"]
        } for r in results])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="test_data.csv", mime="text/csv")