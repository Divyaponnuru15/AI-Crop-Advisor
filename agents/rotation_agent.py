import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# -----------------------------
# Load local .env for local testing only
# -----------------------------
env_path = os.path.join(os.path.dirname(__file__), "..", "ai key", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# -----------------------------
# Get API key from environment
# -----------------------------
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("⚠️ Warning: GROQ_API_KEY is not set! API calls will fail.")
    client = None
else:
    print("✅ GROQ_API_KEY loaded successfully.")
    client = Groq(api_key=api_key)

# -----------------------------
# Function to generate rotation plan
# -----------------------------
def generate_rotation_plan(soil_type, current_crop, season, water_level, lang="en"):
    if not client:
        return {"error": "GROQ_API_KEY not set! Cannot call the Groq API."}

    try:
        # Language mapping
        lang_map = {
            "en": "English",
            "te": "Telugu",
            "hi": "Hindi",
            "kn": "Kannada"
        }
        target_lang = lang_map.get(lang, "English")

        # Prompt for Groq API
        prompt = f"""
Generate crop rotation recommendation.

Return ONLY valid JSON.

Translate both keys and values into {target_lang}.

Format:

{{
"recommended_crops": ["crop1","crop2","crop3"],
"soil_benefit_score": 0.8,
"risk_level": "Low",
"profit_estimation": "Medium",
"explanation": "Short explanation"
}}

Soil Type = {soil_type}
Current Crop = {current_crop}
Season = {season}
Water Level = {water_level}
"""

        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        raw_output = response.choices[0].message.content.strip()

        # Clean markdown if present
        raw_output = raw_output.replace("```json", "").replace("```", "")

        # Extract JSON from response
        match = re.search(r'\{[\s\S]*\}', raw_output)
        if not match:
            return {"error": "Invalid model output", "raw": raw_output}

        structured_output = json.loads(match.group())

        print("MODEL OUTPUT:", structured_output)
        return structured_output

    except Exception as e:
        return {"error": "Model failed", "exception": str(e)}