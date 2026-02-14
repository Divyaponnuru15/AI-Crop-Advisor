import json
import os
from groq import Groq
from dotenv import load_dotenv

# Load local .env if exists (for local testing)
env_path = os.path.join(os.path.dirname(__file__), "..", "ai key", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

api_key = os.environ.get("GROC_API_KEY")
print("Loaded API Key:", api_key)  # Should show your real key locally

client = Groq(api_key=api_key)

def generate_rotation_plan(soil_type, current_crop, season, water_level):
    prompt = f"""
    You are an agricultural AI assistant.

    Farmer details:
    Soil type: {soil_type}
    Current crop: {current_crop}
    Season: {season}
    Water availability: {water_level}

    Respond ONLY in this exact JSON format:

    {{
      "recommended_crops": ["crop1", "crop2", "crop3"],
      "soil_benefit_score": number,
      "risk_level": "Low/Medium/High",
      "profit_estimation": "Low/Medium/High",
      "explanation": "short explanation"
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content

    try:
        structured_output = json.loads(raw_output)
        return structured_output
    except Exception as e:
        return {
            "error": "Model did not return valid JSON",
            "raw_output": raw_output,
            "exception": str(e)
        }
