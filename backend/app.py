from flask import Flask, request, jsonify, render_template
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.rotation_agent import generate_rotation_plan

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    data = request.json

    soil_type = data.get("soil_type")
    current_crop = data.get("current_crop")
    season = data.get("season")
    water_level = data.get("water_level")

    result = generate_rotation_plan(
        soil_type,
        current_crop,
        season,
        water_level
    )

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
