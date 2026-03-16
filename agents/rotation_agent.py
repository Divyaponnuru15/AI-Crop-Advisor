import os
import json
import re
import unicodedata
from groq import Groq

# -----------------------------
# Safe JSON parser
# -----------------------------
def safe_json_parse(raw_output):
    # Remove markdown
    raw_output = raw_output.replace("```json", "").replace("```", "")
    
    # Normalize Unicode
    clean_output = unicodedata.normalize("NFKC", raw_output)
    clean_output = ''.join(c for c in clean_output if not unicodedata.category(c).startswith("C"))

    # Extract JSON using regex
    match = re.search(r'\{.*\}', clean_output, re.DOTALL)
    if not match:
        return None, clean_output

    json_str = match.group()

    # Replace fancy quotes with standard quotes
    json_str = json_str.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")

    # Remove trailing commas before closing braces
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

    try:
        data = json.loads(json_str)
        return data, None
    except Exception as e:
        return None, f"JSON parse error: {e}, raw: {json_str}"

# -----------------------------
# Generate crop rotation plan
# -----------------------------
def generate_rotation_plan(soil_type, current_crop, season, water_level, lang="en"):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set! Cannot call the Groq API."}

    try:
        client = Groq(api_key=api_key)

        # -----------------------------
        # Language-specific settings
        # -----------------------------
        lang_map = {"en": "English", "hi": "Hindi", "te": "Telugu", "kn": "Kannada"}
        target_lang = lang_map.get(lang, "English")

        # Crop name maps
        crop_maps = {
            "hi": {"Moong":"मूंग","Urad":"उड़द","Tur":"तूर","Makka":"मक्का","Wheat":"गेहूं"},
            "te": {"Moong":"మూంగ్","Urad":"ఉరద్","Tur":"తూర్","Makka":"మక్కా","Wheat":"గోధుమ"},
            "kn": {"Moong":"ಹುರಳಿ","Urad":"ಕಾಳುಮರೆ","Tur":"ತೂರು","Makka":"ಮಕ್ಕಾ","Wheat":"ಗೋಧಿ"}
        }

        # Example JSON for prompt (keys in English, values in target language)
        example_json_values = {
            "en": ["Moong","Urad","Tur","Medium","High","Kharif season in loamy soil: Moong, Urad, and Tur improve soil quality and require moderate water."],
            "hi": ["मूंग","उड़द","तूर","मध्यम","अधिक","खरीफ मौसम में दोमट मिट्टी के लिए मूंग, उड़द और तूर की खेती से मिट्टी की गुणवत्ता बढ़ेगी और पानी की आवश्यकता कम होगी।"],
            "te": ["మూంగ్","ఉరద్","తూర్","మధ్యస్థ","అధికం","ఖరీఫ్ రుతులో మట్టి కోసం మూంగ్, ఉరద్ మరియు తూర్ సాగించడం వల్ల మట్టిని నాణ్యత మెరుగుపడుతుంది మరియు నీటి అవసరం తక్కువ ఉంటుంది."],
            "kn": ["ಹುರಳಿ","ಕಾಳುಮರೆ","ಮಕ್ಕಾ","ಮಧ್ಯಮ","ಹೆಚ್ಚು","ಖರೀಫ್ ಋತು ಮತ್ತು ಮರಳು ಮಣ್ಣಿಗೆ ಹುರಳಿ, ಕಾಳುಮರೆ ಮತ್ತು makkā ಬೆಳೆ ಉತ್ತಮವಾಗಿದೆ. ನೀರಿನ ಅವಶ್ಯಕತೆ ಮಧ್ಯಮವಾಗಿದೆ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಬೇಡಿಕೆ ಉತ್ತಮವಾಗಿದೆ."]
        }

        values = example_json_values.get(lang, example_json_values["en"])

        example_json = f"""
{{
"recommended_crops": ["{values[0]}","{values[1]}","{values[2]}"],
"soil_benefit_score": 85,
"risk_level": "{values[3]}",
"profit_estimation": "{values[4]}",
"explanation": "{values[5]}"
}}
"""

        # -----------------------------
        # Prompt
        # -----------------------------
        prompt = f"""
You are an agriculture expert that recommends crop rotation.

Analyze the farm conditions and recommend crops.

All output must be in {target_lang} using proper script.

**Important:** Keep JSON keys exactly as:
"recommended_crops", "soil_benefit_score", "risk_level", "profit_estimation", "explanation".
Do NOT translate these keys. Only translate values (crops, numbers, explanations, labels).
Return ONLY valid JSON, nothing else.

Farm conditions:
Soil Type = {soil_type}
Current Crop = {current_crop}
Season = {season}
Water Level = {water_level}

Example format:

{example_json}
"""

        # -----------------------------
        # Call Groq API
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        raw_output = response.choices[0].message.content.strip()

        # -----------------------------
        # Parse JSON safely
        # -----------------------------
        structured_output, error = safe_json_parse(raw_output)
        if error:
            return {"error": "Model failed", "exception": error, "raw": raw_output}

        # -----------------------------
        # Validate keys
        # -----------------------------
        required_keys = ["recommended_crops", "soil_benefit_score", "risk_level", "profit_estimation", "explanation"]
        for key in required_keys:
            if key not in structured_output:
                return {"error": f"Model output missing '{key}'", "raw": raw_output}

        # -----------------------------
        # Map crop names to proper script if needed
        # -----------------------------
        if lang in crop_maps:
            structured_output["recommended_crops"] = [
                crop_maps[lang].get(c, c) for c in structured_output["recommended_crops"]
            ]

        return structured_output

    except Exception as e:
        return {"error": "Model failed", "exception": str(e)}