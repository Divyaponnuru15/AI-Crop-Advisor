import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# --- Load local .env if exists (for local testing only) ---
local_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(local_env_path):
    load_dotenv(local_env_path)
    print("Loaded local .env")

# --- Get API key from environment variables ---
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set! Set it locally in .env or in Render environment variables.")

print("Loaded API Key:", api_key)

# --- Initialize Groq client ---
client = Groq(api_key=api_key)

# --- Function to generate crop rotation plan ---
def generate_rotation_plan(soil_type, current_crop, season, water_level, lang="en"):
    try:
        lang_map = {
            "en": "English",
            "te": "Telugu",
            "hi": "Hindi",
            "kn": "Kannada"
        }
        target_lang = lang_map.get(lang, "English")

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

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        raw_output = response.choices[0].message.content.strip()

        # Remove any markdown formatting
        raw_output = raw_output.replace("```json", "").replace("```", "")

        match = re.search(r'\{[\s\S]*\}', raw_output)
        if not match:
            return {"error": "Invalid model output", "raw": raw_output}

        clean_json = match.group()
        structured_output = json.loads(clean_json)

        print("MODEL OUTPUT:", structured_output)
        return structured_output

    except Exception as e:
        return {"error": "Model failed", "exception": str(e)}