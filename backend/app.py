from flask import Flask, request, jsonify, render_template, session, redirect,send_file
from crops import (
    normalize_crop,
    normalize_soil,
    normalize_season,
    normalize_water
)
import sys
import os
from fpdf import FPDF
import io
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.rotation_agent import generate_rotation_plan

from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


#  MYSQL CONFIGURATION

app.config['MYSQL_HOST'] = os.getenv("MYSQLHOST", "localhost")
app.config['MYSQL_USER'] = os.getenv("MYSQLUSER", "root")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQLPASSWORD", "")
app.config['MYSQL_DB'] = os.getenv("MYSQLDATABASE")
app.config['MYSQL_PORT'] = int(os.getenv("MYSQLPORT", 3306))
mysql = MySQL(app)

translations = {
    "en": {
        "title": "AI Crop Advisor",
        "soil": "Soil Type",
        "crop": "Current Crop",
        "season": "Season",
        "water": "Water Availability",
        "submit": "Generate Plan",
        "recommended_crops": "Recommended Crops",
        "profit_estimation": "Profit Estimation",
        "risk_level": "Risk Level",
        "soil_benefit_score": "Soil Benefit Score",
        "explanation": "Explanation",

        "soil_placeholder": "Select or type soil type",
        "crop_placeholder": "Select or type current crop",
        "season_placeholder": "Select or type season",
        "water_placeholder": "Select or type water level",

        "soil_options": {
    "Sandy": "Sandy",
    "Loamy": "Loamy",
    "Clay": "Clay",
    "Black": "Black"
},

"crop_options": {
    "Wheat": "Wheat",
    "Rice": "Rice",
    "Maize": "Maize",
    "Sugarcane": "Sugarcane",
    "Pulses": "Pulses",
    
},

"season_options": {
    "Kharif": "Kharif",
    "Rabi": "Rabi",
    "Zadi": "Zadi"
 },
    "season_examples": {
        "Kharif": "Monsoon,June-september",
        "Rabi": "Winter,october-february",
        "Zadi": "Summer,march-June"
    },

"water_options": {
    "Low": "Low",
    "Medium": "Medium",
    "High": "High"
},
"login": "Login",
"register": "Register",
"logout": "Logout",
"dashboard": "Dashboard",
"welcome": "Welcome",
"name": "Name",
"email": "Email",
"password": "Password",
"member_since": "Member Since",
"home": "Home",
"how_it_works": "How It Works",
"about_text": "The AI Multi-Crop Planner analyzes your soil type, season, water availability, and current crop. Based on this information, it recommends suitable crops along with profit estimation and risk level to help farmers make smarter decisions.",
"crop_history": "Crop History",
"soil_col": "Soil",
"crop_col": "Crop",
"season_col": "Season",
"water_col": "Water",
"recommendation_col": "Recommendation",
"date_col": "Date",
"action": "Action",
"delete": "Delete",
"crop_charts": "Crop Charts",
"explanation": "Explanation",
"crop_details": "Crop Details",
"tips": "Tips",
"explanation_text": "These crops are selected based on soil type, season, and water availability to maximize yield and reduce risk.",
"tips_list": [
        "Use proper irrigation methods",
        "Rotate crops for better soil health",
        "Monitor weather conditions regularly"
    ]

  },


    "te": {
    "title": "ఏఐ పంట సలహాదారు",
    "soil": "మట్టి రకం",
    "crop": "ప్రస్తుత పంట",
    "season": "కాలం",
    "water": "నీటి లభ్యత",
    "submit": "పథకం సృష్టించు",
    "recommended_crops": "సిఫార్సు చేసిన పంటలు",
    "profit_estimation": "లాభ అంచనా",
    "risk_level": "ప్రమాద స్థాయి",
    "soil_benefit_score": "మట్టి లాభ స్కోరు",
    "explanation": "వివరణ",

    "soil_placeholder": "మట్టి రకం ఎంచుకోండి లేదా టైప్ చేయండి",
    "crop_placeholder": "ప్రస్తుత పంట ఎంచుకోండి లేదా టైప్ చేయండి",
    "season_placeholder": "కాలం ఎంచుకోండి లేదా టైప్ చేయండి",
    "water_placeholder": "నీటి స్థాయి ఎంచుకోండి లేదా టైప్ చేయండి",

    "soil_options": {
        "Sandy": "ఇసుక మట్టి",
        "Loamy": "లోమీ మట్టి",
        "Clay": "చిక్కటి మట్టి",
        "Black": "నల్ల మట్టి"
    },
    "crop_options": {
    "Wheat": "గోధుమ",
    "Rice": "బియ్యం",
    "Maize": "మొక్కజొన్న",
    "Sugarcane": "చెరకు",
    "Pulses": "పప్పులు",
    
},

    "season_options": {
        "Kharif": "ఖరీఫ్",
        "Rabi": "రబీ",
        "Zadi": "జాది"
    },

     "season_examples": {
        "Kharif": "వర్షాకాలం, జూన్–సెప్టెంబర్",
        "Rabi": "చలి కాలం, అక్టోబర్–ఫిబ్రవరి",
        "Zadi": "వేసవి, మార్చ్–జూన్"

    },
    "water_options": {
        "Low": "తక్కువ",
        "Medium": "మధ్యస్థ",
        "High": "ఎక్కువ"
    },

    "login": "లాగిన్",
    "register": "నమోదు",
    "logout": "లాగౌట్",
    "dashboard": "డాష్‌బోర్డ్",
    "welcome": "స్వాగతం",

    "name": "పేరు",
    "email": "ఇమెయిల్",
    "password": "పాస్‌వర్డ్",

    "member_since": "సభ్యత్వం ప్రారంభం",
    "home": "హోమ్",
"how_it_works": "ఇది ఎలా పనిచేస్తుంది",
"about_text": "ఏఐ మల్టీ-క్రాప్ ప్లానర్ మీ మట్టి రకం, సీజన్, నీటి లభ్యత మరియు ప్రస్తుత పంటను విశ్లేషిస్తుంది. ఈ సమాచారంపై ఆధారపడి సరైన పంటలను లాభ అంచనా మరియు ప్రమాద స్థాయితో సిఫార్సు చేస్తుంది.",

"crop_history": "పంట చరిత్ర",
"soil_col": "మట్టి",
"crop_col": "పంట",
"season_col": "కాలం",
"water_col": "నీరు",
"recommendation_col": "సిఫార్సు",
"date_col": "తేదీ",
"action": "చర్య",
"delete": "తొలగించు",
"crop_charts": "పంటల చార్ట్",
"explanation": "వివరణ",
"crop_details": "పంట వివరాలు",
"tips": "సూచనలు",
"explanation_text": "ఈ పంటలు మట్టి, సీజన్ మరియు నీటి లభ్యత ఆధారంగా ఎంపిక చేయబడ్డాయి...",
"tips_list": [
"సరైన సాగు విధానాలను ఉపయోగించండి",
"మట్టిని ఆరోగ్యంగా ఉంచడానికి పంటల రోటేషన్ చేయండి",
"వాతావరణ పరిస్థితులను నియమితంగా గమనించండి"
 ],

},


"hi": {
    "title": "एआई फसल सलाहकार",
    "soil": "मिट्टी का प्रकार",
    "crop": "वर्तमान फसल",
    "season": "मौसम",
    "water": "पानी की उपलब्धता",
    "submit": "योजना बनाएं",
    "recommended_crops": "अनुशंसित फसलें",
    "profit_estimation": "लाभ अनुमान",
    "risk_level": "जोखिम स्तर",
    "soil_benefit_score": "मिट्टी लाभ स्कोर",
    "explanation": "व्याख्या",

    "soil_placeholder": "मिट्टी का प्रकार चुनें या लिखें",
    "crop_placeholder": "वर्तमान फसल चुनें या लिखें",
    "season_placeholder": "मौसम चुनें या लिखें",
    "water_placeholder": "पानी का स्तर चुनें या लिखें",

    "soil_options": {
        "Sandy": "रेतीली मिट्टी",
        "Loamy": "दोमट मिट्टी",
        "Clay": "चिकनी मिट्टी",
        "Black": "काली मिट्टी"
    },
    "crop_options": {
        "Wheat": "गेहूं",
        "Rice": "चावल",
        "Maize": "मक्का",
        "Sugarcane": "गन्ना",
        "Pulses": "दालें",
        
    },

    "season_options": {
        "Kharif": "खरीफ",
        "Rabi": "रबी",
        "Zadi": "ज़ादी"       
    },

    "season_examples": {
        "Kharif": "बरसाती मौसम, जून–सितंबर",
        "Rabi": "सर्दी, अक्टूबर–फरवरी",
        "Zadi": "गर्मी, मार्च–जून"   
    },

    "water_options": {
        "Low": "कम",
        "Medium": "मध्यम",
        "High": "अधिक"
    },

    "login": "लॉगिन",
"register": "रजिस्टर",
"logout": "लॉगआउट",
"dashboard": "डैशबोर्ड",
"welcome": "स्वागत",
"name": "नाम",
"email": "ईमेल",
"password": "पासवर्ड",
"member_since": "सदस्यता प्रारंभ",

    "home": "होम",
     "how_it_works": "यह कैसे काम करता है",
"about_text": "एआई मल्टी-क्रॉप प्लानर आपकी मिट्टी के प्रकार, मौसम, पानी की उपलब्धता और वर्तमान फसल का विश्लेषण करता है। इस जानकारी के आधार पर यह लाभ अनुमान और जोखिम स्तर के साथ उपयुक्त फसलों की सिफारिश करता है।",

"crop_history": "फसल इतिहास",
"soil_col": "मिट्टी",
"crop_col": "फसल",
"season_col": "मौसम",
"water_col": "पानी",
"recommendation_col": "सिफारिश",
"date_col": "तारीख",
"action": "कार्रवाई",
"delete": "हटाएं",
"crop_charts": "फसल चार्ट",
"explanation": "व्याख्या",
"crop_details": "फसल विवरण",
"tips": "सुझाव",

"explanation_text": "इन फसलों का चयन मिट्टी के प्रकार, मौसम और पानी की उपलब्धता के आधार पर किया गया है ताकि उत्पादन बढ़े और जोखिम कम हो।",
"tips_list": [
"सही सिंचाई विधियों का उपयोग करें",
"मिट्टी के स्वास्थ्य के लिए फसल चक्रीकरण करें",
"मौसम की परिस्थितियों पर नियमित रूप से नज़र रखें"
 ],

},
"kn": {
    "title": "ಎಐ ಬೆಳೆ ಸಲಹೆಗಾರ",
    "soil": "ಮಣ್ಣಿನ ಪ್ರಕಾರ",
    "crop": "ಪ್ರಸ್ತುತ ಬೆಳೆ",
    "season": "ಋತು",
    "water": "ನೀರಿನ ಲಭ್ಯತೆ",
    "submit": "ಯೋಜನೆ ರಚಿಸಿ",
    "recommended_crops": "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು",
    "profit_estimation": "ಲಾಭ ಅಂದಾಜು",
    "risk_level": "ಜೊಖಿಂ ಮಟ್ಟ",
    "soil_benefit_score": "ಮಣ್ಣು ಲಾಭ ಅಂಕ",
    "explanation": "ವಿವರಣೆ",

    "soil_placeholder": "ಮಣ್ಣಿನ ಪ್ರಕಾರ ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ",
    "crop_placeholder": "ಪ್ರಸ್ತುತ ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ",
    "season_placeholder": "ಋತು ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ",
    "water_placeholder": "ನೀರಿನ ಮಟ್ಟ ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ",

    "soil_options": {
        "Sandy": "ಮರಳು ಮಣ್ಣು",
        "Loamy": "ಲೋಮಿ ಮಣ್ಣು",
        "Clay": "ಚಿಕ್ಕಣಿ ಮಣ್ಣು",
        "Black": "ಕರಿ ಮಣ್ಣು"
    },

    "crop_options": {
        "Wheat": "ಗೋಧಿ",
        "Rice": "ಅಕ್ಕಿ",
        "Maize": "ಮಕ್ಕಿ ಜೋಳ",
        "Sugarcane": "ಕಬ್ಬು",
        "Pulses": "ಬೇಳೆ"
        
    },

    "season_options": {
        "Kharif": "ಖರೀಫ್",
        "Rabi": "ರಬೀ",
        "Zadi": "ಜಾದಿ"
    },

    "season_examples": {
        "Kharif": "ಮಳೆಗಾಲ, ಜೂನ್–ಸೆಪ್ಟೆಂಬರ್",
        "Rabi": "ಚಳಿಗಾಲ, ಅಕ್ಟೋಬರ್–ಫೆಬ್ರುವರಿ",
        "Zadi": "ಬೆಸಿಗೆ, ಮಾರ್ಚ್–ಜೂನ್"
    },

    "water_options": {
        "Low": "ಕಡಿಮೆ",
        "Medium": "ಮಧ್ಯಮ",
        "High": "ಹೆಚ್ಚು"
    },

    "login": "ಲಾಗಿನ್",
    "register": "ನೋಂದಣಿ",
    "logout": "ಲಾಗ್ ಔಟ್",
    "dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    "welcome": "ಸ್ವಾಗತ",
    "name": "ಹೆಸರು",
    "email": "ಇಮೇಲ್",
    "password": "ಪಾಸ್‌ವರ್ಡ್",
    "member_since": "ಸದಸ್ಯತ್ವ ಆರಂಭ",

    "home": "ಹೋಮ್",
    "how_it_works": "ಇದು ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ",
    "about_text": "ಎಐ ಮಲ್ಟಿ-ಕ್ರಾಪ್ ಪ್ಲಾನರ್ ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರಕಾರ, ಋತು, ನೀರಿನ ಲಭ್ಯತೆ ಮತ್ತು ಪ್ರಸ್ತುತ ಬೆಳೆಗಳನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ. ಈ ಮಾಹಿತಿಯ ಆಧಾರದಲ್ಲಿ ಲಾಭ ಅಂದಾಜು ಮತ್ತು ಅಪಾಯ ಮಟ್ಟದೊಂದಿಗೆ ಸೂಕ್ತ ಬೆಳೆಗಳನ್ನು ಶಿಫಾರಸು ಮಾಡುತ್ತದೆ.",

    "crop_history": "ಬೆಳೆ ಇತಿಹಾಸ",
    "soil_col": "ಮಣ್ಣು",
    "crop_col": "ಬೆಳೆ",
    "season_col": "ಋತು",
    "water_col": "ನೀರು",
    "recommendation_col": "ಶಿಫಾರಸು",
    "date_col": "ದಿನಾಂಕ",
    "action": "ಕ್ರಿಯೆ",
    "delete": "ಅಳಿಸು",
    "crop_charts": "ಬೆಳೆ ಚಾರ್ಟ್",
    "crop_details": "ಬೆಳೆ ವಿವರಗಳು",
    "tips": "ಸಲಹೆಗಳು",
    "explanation_text": "ಈ ಬೆಳೆಗಳನ್ನು ಮಣ್ಣಿನ ಪ್ರಕಾರ, ಋತು ಮತ್ತು ನೀರಿನ ಲಭ್ಯತೆ ಆಧರಿಸಿ ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ, ಉತ್ಪಾದನೆ ಹೆಚ್ಚಿಸಲು ಮತ್ತು ಅಪಾಯವನ್ನು ಕಡಿಮೆ ಮಾಡಲು.",
    "tips_list": [
      "ಸರಿಯಾದ ನಿಬಂಧನೆ ವಿಧಾನಗಳನ್ನು ಬಳಸಿ",
      "ಮಣ್ಣಿನ ಆರೋಗ್ಯಕ್ಕಾಗಿ ಬೆಳೆ ರೋಟೇಶನ್ ಮಾಡಿ",
      "ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ನಿಯಮಿತವಾಗಿ ಗಮನಿಸಿ"
 ]
},
}

value_translations = {
    "te": {
        "Low": "తక్కువ",
        "Medium": "మధ్యస్థం",
        "High": "ఎక్కువ"
    },
    "hi": {
        "Low": "कम",
        "Medium": "मध्यम",
        "High": "अधिक"
    },
    "kn": {
        "Low": "ಕಡಿಮೆ",
        "Medium": "ಮಧ್ಯಮ",
        "High": "ಹೆಚ್ಚು"
    }
}

def translate_keys(result, lang):

    if lang == "en":
        return result

    text = translations.get(lang, {})
    value_map = text.get("water_options", {})

    translated = {}

    for key, value in result.items():

        new_key = text.get(key, key)

        # translate Low / Medium / High
        if isinstance(value, str) and value.title() in value_map:
            value = value_map[value.title()]

        translated[new_key] = value

    return translated
def reverse_translate(value, field, lang):
    if lang == "en":
        return value

    options = translations.get(lang, {}).get(field, {})

    for eng, translated in options.items():
        if value.strip() == translated.strip():  
            return eng

    return value


def translate_crops(crops_str, lang):
    if not crops_str:
        return "N/A"
    crops = [crop.strip() for crop in crops_str.split(",")]
    if lang == "en":
        return ", ".join(crops)

    text = translations.get(lang, {})
    crop_options = text.get("crop_options", {})

    translated = []
    for crop in crops:
        translated.append(crop_options.get(crop, crop))
    return ", ".join(translated)


@app.route("/")
def home():
    lang = session.get("lang", "en")  # Default English
    text = translations.get(lang, translations["en"])
    return render_template("index.html", text=text, lang=lang)

@app.route("/set-language", methods=["POST"])
def set_language():
    selected_lang = request.form.get("language")
    session["lang"] = selected_lang
    return redirect("/")

@app.route("/generate-plan", methods=["POST"])
def generate_plan():

    data = request.json
    lang = session.get("lang", "en")

    # Reverse-translate inputs if not English
    soil_input = data.get("soil_type", "").strip()
    crop_input = data.get("current_crop", "").strip()
    season_input = data.get("season", "").strip()
    water_input = data.get("water_level", "").strip()

    soil_type = normalize_soil(reverse_translate(soil_input, "soil_options", lang))
    current_crop = normalize_crop(reverse_translate(crop_input, "crop_options", lang))
    season = normalize_season(reverse_translate(season_input, "season_options", lang))
    water_level = normalize_water(reverse_translate(water_input, "water_options", lang))

    # Dynamic validation
    if not soil_type:
     return jsonify({"error": "Please enter valid soil type"})
    if not current_crop:
     return jsonify({"error": "Please enter valid crop name"})
    if not season:
     return jsonify({"error": "Please enter valid season"})
    if not water_level:
     return jsonify({"error": "Please enter valid water level"})

       
    try:

        result = generate_rotation_plan(
            soil_type,
            current_crop,
            season,
            water_level,
            lang=lang
        )

        print("MODEL OUTPUT:", result)

        # Check valid JSON
        if not isinstance(result, dict):
            return jsonify({
                "error": "Model did not return valid JSON"
            })
        
        # SAVE HISTORY ONLY IF USER LOGGED IN
        if "user_id" in session:
            user_id = session["user_id"]

            cur = mysql.connection.cursor()
            recommendations = result.get("recommended_crops", [])  # fallback to empty list

            cur.execute("""
            INSERT INTO crop_history
            (user_id, soil_type, current_crop, season, water_level, recommendation, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,NOW())
            """, (
            user_id,
            soil_type,
            current_crop,
            season,
            water_level,
            ",".join(recommendations)
            ))

            mysql.connection.commit()
            cur.close()
        else:
            print("Guest user, crop history not saved.")

        

        # Translate keys
        translated_result = translate_keys(result, lang)

        return jsonify(translated_result)

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": "Server Error"
        })


@app.route("/register", methods=["GET","POST"])
def register():

    lang = session.get("lang", "en")
    text = translations.get(lang, translations["en"])

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
            (name,email,hashed_password)
        )

        mysql.connection.commit()
        cur.close()

        return redirect("/login")

    return render_template("register.html",text=text)

@app.route("/login", methods=["GET","POST"])
def login():

    lang = session.get("lang", "en")
    text = translations.get(lang, translations["en"])

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3],password):

            session["user_id"]=user[0]
            session["user_name"]=user[1]

            return redirect("/dashboard")

        else:
            return "Invalid credentials"

    return render_template("login.html",text=text)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
from collections import Counter

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    lang=session.get("lang","en")
    text=translations.get(lang,translations["en"])

    user_id=session["user_id"]

    cur=mysql.connection.cursor()

    # User Info
    cur.execute(
    "SELECT name,email,created_at FROM users WHERE id=%s",
    (user_id,)
    )

    user = cur.fetchone()

    
    if user and user[2] is None:
     from datetime import datetime
     user = (user[0], user[1], datetime.now())
   

    # Crop History
    cur.execute("""
    SELECT soil_type,current_crop,season,water_level,recommendation,created_at,id
    FROM crop_history
    WHERE user_id=%s
    ORDER BY id DESC
    """,(user_id,))

    history=cur.fetchall()

    cur.close()

    # --- Calculate Soil Benefit Scores dynamically ---
    soil_benefits_dict = {}

    for row in history:
        soil = (row[0] or "").lower()
        recommendations = (row[4] or "").split(",")

        for crop in recommendations:
            crop = crop.strip().lower()

            if not crop:
               continue

        # Initialize
            if crop not in soil_benefits_dict:
               soil_benefits_dict[crop] = 0

        # Soil weight
            soil_weights = {
               "loamy": 3,
               "black": 2,
                "clay": 1.5,
                "sandy": 1
            }

            score = soil_weights.get(soil, 1)

        # Diversity bonus
            score += len(set(recommendations)) * 0.5

        
            soil_benefits_dict[crop] += score

    
    if not soil_benefits_dict:
        soil_benefits_dict ={}

    # --- Prepare data for Chart.js ---
    labels = list(soil_benefits_dict.keys())
    soil_benefits = list(soil_benefits_dict.values())

    

    return render_template("dashboard.html",
                           user=user,
                           history=history,
                           text=text,
                           labels=labels,
                           soil_benefits=soil_benefits)
@app.route("/delete-history/<int:id>")
def delete_history(id):

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM crop_history WHERE id=%s",(id,))

    mysql.connection.commit()

    cur.close()

    return redirect("/dashboard")


@app.route("/offline.html")
def offline():
    return render_template("offline.html")




from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics


import ast
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase import ttfonts, pdfmetrics
import io, os

@app.route('/download_result', methods=['POST'])
def download_result():
    lang = session.get("lang", "en")
    text = translations.get(lang, translations["en"])

    # Read form values
    crop = request.form.get('crop', 'N/A')
    soil = request.form.get('soil', 'N/A')
    water = request.form.get('water', 'N/A')
    season = request.form.get('season', 'N/A')
    recommended_raw = request.form.get('recommended', '')

    recommended_list = [r.strip() for r in recommended_raw.split(",") if r.strip()]
    recommended_str = ", ".join(recommended_list) if recommended_list else "N/A"

    # Translate recommended crops
    recommended_translated = translate_crops(recommended_str, lang)

    # Translate other fields for PDF
    if lang != "en":
        crop = text.get("crop_options", {}).get(crop.capitalize(), crop)
        soil = text.get("soil_options", {}).get(soil.capitalize(), soil)
        season = text.get("season_options", {}).get(season.capitalize(), season)
        water = value_translations.get(lang, {}).get(water.capitalize(), water)

    # --- PDF Setup ---
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595, 842))  # A4 size

    # Font setup
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(base_dir, "fonts")

    if lang == "te":
        font_path = os.path.join(font_dir, "NotoSansTelugu-Regular.ttf")
        font_name = "Telugu"
    elif lang == "hi":
        font_path = os.path.join(font_dir, "NotoSansDevanagari-Regular.ttf")
        font_name = "Hindi"
    elif lang == "kn":
        font_path = os.path.join(font_dir, "NotoSansKannada-Regular.ttf")
        font_name = "Kannada"
    else:
        font_path = os.path.join(font_dir, "DejaVuSans.ttf")
        font_name = "Default"

    pdfmetrics.registerFont(ttfonts.TTFont(font_name, font_path))
    c.setFont(font_name, 22)
       

    # --- Header ---
    c.setFillColorRGB(0.2, 0.6, 0.3)
    c.rect(0, 770, 595, 50, fill=1)  # Full width header
    c.setFillColorRGB(1, 1, 1)
    c.drawCentredString(297, 790, text["title"])
    c.setFillColorRGB(0, 0, 0)

    y = 730
    line_height = 22  # More spacing

    #  Crop Details Section 
    c.setFont(font_name, 23)
    c.drawString(50, y, text["crop_details"])
    y -= line_height
    
    y -= 20

    c.setFont(font_name, 16)
    c.drawString(50, y, f"{text['crop']}: {crop}")
    y -= line_height
    c.drawString(50, y, f"{text['soil']}: {soil}")
    y -= line_height
    c.drawString(50, y, f"{text['water']}: {water}")
    y -= line_height
    c.drawString(50, y, f"{text['season']}: {season}")
    y -= line_height
    c.line(50, y, 545, y)

    # --- Recommended Crops ---
    c.setFont(font_name, 20)
    y -= 20
    c.drawString(50, y, text["recommended_crops"])
    y -= 30
    c.setFont(font_name, 16)
    c.drawString(50, y, recommended_translated)
    y -= line_height
    c.line(50, y, 545, y)

    
    # --- Explanation ---
    c.setFont(font_name, 20)
    y -= 20
    c.drawString(50, y, text["explanation"])
    y -= 30
    
    text_obj = c.beginText(50, y)
    text_obj.setFont(font_name, 14)
    
    line = ""
    max_width = 450  # max width of line
    
    for word in text["explanation_text"].split(" "):
        test_line = line + word + " "
        
        if pdfmetrics.stringWidth(test_line, font_name, 14) < max_width:
            line = test_line
        else:
            text_obj.textLine(line)
            line = word + " "
    
    
    if line:
        text_obj.textLine(line)
    
    c.drawText(text_obj)
    
    y = text_obj.getY() - 10
    c.line(50, y, 545, y)
    y -= 20 

    # --- Tips ---
    
    c.setFont(font_name, 20)
    
    c.drawString(50, y, text["tips"])
    y -= 24
    c.setFont(font_name, 16)
    for tip in text.get("tips_list", []):
        c.drawString(60, y, f"- {tip}")
        y -= line_height

    # --- Footer ---
    c.setFont(font_name, 16)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(50, 40, f"Generated on: {datetime.now().strftime('%d-%m-%Y')}")
    c.drawString(50, 25, "AI Crop Advisor Report")

    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="AI_Crop_Result.pdf",
        mimetype='application/pdf'
    )
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)