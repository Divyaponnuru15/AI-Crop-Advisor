from flask import Flask, request, jsonify, render_template, session, redirect
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.rotation_agent import generate_rotation_plan

from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key =  "my_crop_planner_secret_123"
load_dotenv()

# 👇 ADD MYSQL CONFIGURATION HERE

app.config['MYSQL_HOST'] = os.getenv("MYSQLHOST", "localhost")
app.config['MYSQL_USER'] = os.getenv("MYSQLUSER", "root")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQLPASSWORD", "")
app.config['MYSQL_DB'] = os.getenv("MYSQLDATABASE")
app.config['MYSQL_PORT'] = int(os.getenv("MYSQLPORT", 3306))
mysql = MySQL(app)

translations = {
    "en": {
        "title": "AI Crop Rotation Planner",
        "soil": "Soil Type",
        "crop": "Current Crop",
        "season": "Season",
        "water": "Water Availability",
        "submit": "Generate Plan",
        "recommended": "Recommended Crops",
        "profit": "Profit Estimation",
        "risk": "Risk Level",
        "soil_score": "Soil Benefit Score",
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
    "Oats": "Oats"
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
"explanation": "Explanation"

  },


    "te": {
    "title": "ఏఐ పంట మార్పిడి ప్రణాళిక",
    "soil": "మట్టి రకం",
    "crop": "ప్రస్తుత పంట",
    "season": "కాలం",
    "water": "నీటి లభ్యత",
    "submit": "పథకం సృష్టించు",
    "recommended": "సిఫార్సు చేసిన పంటలు",
    "profit": "లాభ అంచనా",
    "risk": "ప్రమాద స్థాయి",
    "soil_score": "మట్టి లాభ స్కోరు",
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
    "Oats": "ఓట్స్"
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
"about_text": "AI మల్టీ-క్రాప్ ప్లానర్ మీ మట్టి రకం, సీజన్, నీటి లభ్యత మరియు ప్రస్తుత పంటను విశ్లేషిస్తుంది. ఈ సమాచారంపై ఆధారపడి సరైన పంటలను లాభ అంచనా మరియు ప్రమాద స్థాయితో సిఫార్సు చేస్తుంది.",

"crop_history": "పంట చరిత్ర",
"soil_col": "మట్టి",
"crop_col": "పంట",
"season_col": "కాలం",
"water_col": "నీరు",
"recommendation_col": "సిఫార్సు",
"date_col": "తేదీ",
"action": "చర్య",
"delete": "తొలగించు",
"explanation": "వివరణ"
},


"hi": {
    "title": "एआई फसल चक्र योजना",
    "soil": "मिट्टी का प्रकार",
    "crop": "वर्तमान फसल",
    "season": "मौसम",
    "water": "पानी की उपलब्धता",
    "submit": "योजना बनाएं",
    "recommended": "अनुशंसित फसलें",
    "profit": "लाभ अनुमान",
    "risk": "जोखिम स्तर",
    "soil_score": "मिट्टी लाभ स्कोर",
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
        "Oats": "जई"
    },

    "season_options": {
        "Kharif": "खरीफ",
        "Rabi": "रबी",
        "Zadi": "ज़ादी"       # <-- key must match season_examples
    },

    "season_examples": {
        "Kharif": "बरसाती मौसम, जून–सितंबर",
        "Rabi": "सर्दी, अक्टूबर–फरवरी",
        "Zadi": "गर्मी, मार्च–जून"   # <-- same key as season_options
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
"about_text": "AI मल्टी-क्रॉप प्लानर आपकी मिट्टी के प्रकार, मौसम, पानी की उपलब्धता और वर्तमान फसल का विश्लेषण करता है। इस जानकारी के आधार पर यह लाभ अनुमान और जोखिम स्तर के साथ उपयुक्त फसलों की सिफारिश करता है।",

"crop_history": "फसल इतिहास",
"soil_col": "मिट्टी",
"crop_col": "फसल",
"season_col": "मौसम",
"water_col": "पानी",
"recommendation_col": "सिफारिश",
"date_col": "तारीख",
"action": "कार्रवाई",
"delete": "हटाएं",
"explanation": "व्याख्या"

},
"kn": {
    "title": "ಎಐ ಬೆಳೆ ಪರಿವರ್ತನೆ ಯೋಜನೆ",
    "soil": "ಮಣ್ಣಿನ ಪ್ರಕಾರ",
    "crop": "ಪ್ರಸ್ತುತ ಬೆಳೆ",
    "season": "ಋತು",
    "water": "ನೀರಿನ ಲಭ್ಯತೆ",
    "submit": "ಯೋಜನೆ ರಚಿಸಿ",
    "recommended": "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು",
    "profit": "ಲಾಭ ಅಂದಾಜು",
    "risk": "ಜೊಖಿಂ ಮಟ್ಟ",
    "soil_score": "ಮಣ್ಣು ಲಾಭ ಅಂಕ",
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
        "Pulses": "ಬೇಳೆ",
        "Oats": "ಓಟ್ಸ್"
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
    "about_text": "AI ಮಲ್ಟಿ-ಕ್ರಾಪ್ ಪ್ಲಾನರ್ ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರಕಾರ, ಋತು, ನೀರಿನ ಲಭ್ಯತೆ ಮತ್ತು ಪ್ರಸ್ತುತ ಬೆಳೆಗಳನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ. ಈ ಮಾಹಿತಿಯ ಆಧಾರದಲ್ಲಿ ಲಾಭ ಅಂದಾಜು ಮತ್ತು ಅಪಾಯ ಮಟ್ಟದೊಂದಿಗೆ ಸೂಕ್ತ ಬೆಳೆಗಳನ್ನು ಶಿಫಾರಸು ಮಾಡುತ್ತದೆ.",

    "crop_history": "ಬೆಳೆ ಇತಿಹಾಸ",
    "soil_col": "ಮಣ್ಣು",
    "crop_col": "ಬೆಳೆ",
    "season_col": "ಋತು",
    "water_col": "ನೀರು",
    "recommendation_col": "ಶಿಫಾರಸು",
    "date_col": "ದಿನಾಂಕ",
    "action": "ಕ್ರಿಯೆ",
    "delete": "ಅಳಿಸು"
},
}
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

    soil_type = data.get("soil_type")
    current_crop = data.get("current_crop")
    season = data.get("season")
    water_level = data.get("water_level")

    lang = session.get("lang", "en")

    try:

        result = generate_rotation_plan(
            soil_type,
            current_crop,
            season,
            water_level,
            lang=lang
        )

        print("MODEL OUTPUT:", result)  # Debug

        # ✅ Check valid JSON
        if not isinstance(result, dict):
            return jsonify({
                "error": "Model did not return valid JSON"
            })

        # ✅ SAVE HISTORY
        if "user_id" in session:

            user_id = session["user_id"]

            cur = mysql.connection.cursor()

            cur.execute("""
            INSERT INTO crop_history
            (user_id, soil_type, current_crop, season, water_level, recommendation)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,(user_id,soil_type,current_crop,season,water_level,str(result)))

            mysql.connection.commit()
            cur.close()

        return jsonify(result)

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

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    lang=session.get("lang","en")
    text=translations.get(lang,translations["en"])

    user_id=session["user_id"]

    cur=mysql.connection.cursor()

    # User Info
    cur.execute("SELECT name,email,created_at FROM users WHERE id=%s",(user_id,))
    user=cur.fetchone()

    # Crop History
    cur.execute("""
SELECT soil_type,current_crop,season,water_level,recommendation,created_at,id
FROM crop_history
WHERE user_id=%s
ORDER BY id DESC
""",(user_id,))

    history=cur.fetchall()

    cur.close()

    return render_template("dashboard.html",
                           user=user,
                           history=history,
                           text=text)
@app.route("/delete-history/<int:id>")
def delete_history(id):

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM crop_history WHERE id=%s",(id,))

    mysql.connection.commit()

    cur.close()

    return redirect("/dashboard")

# <-- Add this at the bottom of app.py before app.run()
@app.route("/offline.html")
def offline():
    return render_template("offline.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)