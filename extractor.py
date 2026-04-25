import os
import time
import json
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


# ─────────────────────────────────────────────
# 1. PDF TEXT EXTRACTION
# ─────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Read every page of the PDF and return all text as one string.
    Works for both digital PDFs and scanned PDFs (basic text layer).
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num, page in enumerate(doc):
        full_text += f"\n\n--- PAGE {page_num + 1} ---\n"
        full_text += page.get_text()
    doc.close()
    return full_text.strip()


# ─────────────────────────────────────────────
# 2. EXTRACT CASE DETAILS FROM JUDGMENT
# ─────────────────────────────────────────────

def extract_case_details(text: str) -> dict:
    """
    Ask Gemini to extract structured case information from judgment text.
    Returns a dict of fields, each with a value and confidence score.
    """

    prompt = f"""
You are an expert legal document analyst for the Karnataka Government.

Read the following court judgment text carefully and extract the key details.
Respond ONLY with a valid JSON object — no explanation, no markdown, no extra text.

The JSON must have exactly these keys:
{{
  "case_number": {{"value": "...", "confidence": "high/medium/low"}},
  "court_name": {{"value": "...", "confidence": "high/medium/low"}},
  "order_date": {{"value": "...", "confidence": "high/medium/low"}},
  "petitioner": {{"value": "...", "confidence": "high/medium/low"}},
  "respondent": {{"value": "...", "confidence": "high/medium/low"}},
  "judge_name": {{"value": "...", "confidence": "high/medium/low"}},
  "case_type": {{"value": "...", "confidence": "high/medium/low"}},
  "key_directives": {{"value": "...", "confidence": "high/medium/low"}},
  "appeal_deadline": {{"value": "...", "confidence": "high/medium/low"}},
  "compliance_timeline": {{"value": "...", "confidence": "high/medium/low"}}
}}

Rules:
- If a field is not found, set value to "Not found" and confidence to "low"
- key_directives: summarize ALL orders/directions given by the court in 3-5 bullet points
- appeal_deadline: extract or infer the limitation period for filing an appeal
- compliance_timeline: any deadlines mentioned for government action
- Be concise but complete

JUDGMENT TEXT:
{text[:6000]}
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Clean up if Gemini wraps in markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        # Return a safe fallback if JSON parsing fails
        return {
            field: {"value": "Could not extract", "confidence": "low"}
            for field in [
                "case_number", "court_name", "order_date", "petitioner",
                "respondent", "judge_name", "case_type", "key_directives",
                "appeal_deadline", "compliance_timeline"
            ]
        }
    except Exception as e:
        return {"error": {"value": str(e), "confidence": "low"}}


# ─────────────────────────────────────────────
# 3. GENERATE ACTION PLAN
# ─────────────────────────────────────────────

def generate_action_plan(text: str, case_details: dict) -> list:
    """
    Ask Gemini to generate a structured action plan for government officers
    based on the judgment text and already-extracted case details.
    Returns a list of action items.
    """

    directives = case_details.get("key_directives", {}).get("value", "")
    order_date = case_details.get("order_date", {}).get("value", "")
    appeal_deadline = case_details.get("appeal_deadline", {}).get("value", "")

    prompt = f"""
You are a senior legal advisor to the Karnataka Government.

Based on this court judgment, generate a clear action plan for government officers.
Respond ONLY with a valid JSON array — no explanation, no markdown, no extra text.

Each item in the array must have exactly these keys:
{{
  "action_type": "Comply / Consider Appeal / Monitor / File Response / No Action Required",
  "description": "Clear 1-2 sentence description of what needs to be done",
  "deadline": "Specific date or timeframe, e.g. '30 days from order date' or 'By DD/MM/YYYY'",
  "department": "Which government department is responsible",
  "priority": "High / Medium / Low"
}}

Generate between 2 to 6 action items based on the judgment.

Key information already extracted:
- Order date: {order_date}
- Key directives: {directives}
- Appeal deadline: {appeal_deadline}

FULL JUDGMENT TEXT:
{text[:5000]}
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Clean markdown if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        actions = json.loads(raw)

        # Ensure it's always a list
        if isinstance(actions, dict):
            actions = [actions]

        return actions

    except json.JSONDecodeError:
        return [{
            "action_type": "Manual Review Required",
            "description": "AI could not parse action plan. Please review judgment manually.",
            "deadline": "As soon as possible",
            "department": "Legal Department",
            "priority": "High"
        }]
    except Exception as e:
        return [{
            "action_type": "Error",
            "description": f"Error generating action plan: {str(e)}",
            "deadline": "N/A",
            "department": "N/A",
            "priority": "High"
        }]


# ─────────────────────────────────────────────
# 4. FULL PIPELINE — call this from app.py
# ─────────────────────────────────────────────

def process_judgment(pdf_path: str) -> tuple:
    """
    Full pipeline:
      1. Extract text from PDF
      2. Extract case details with Gemini
      3. Generate action plan with Gemini
    Returns (case_details dict, action_plans list, raw_text string)
    """
    print(f"[NyayaSetu] Reading PDF: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)

    print("[NyayaSetu] Extracting case details with Gemini...")
    case_details = extract_case_details(raw_text)

    print("[NyayaSetu] Waiting before second API call...")
    time.sleep(30)

    print("[NyayaSetu] Generating action plan with Gemini...")
    action_plans = generate_action_plan(raw_text, case_details)

    return case_details, action_plans, raw_text
