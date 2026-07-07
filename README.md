# 🌱 AI Crop Advisor

An AI-powered crop recommendation web application built with **Flask**, **Groq API**, and **Supabase**. The application analyzes farming conditions such as soil type, current crop, season, and water availability to generate intelligent crop recommendations that help farmers make informed agricultural decisions.

## 🚀 Live Demo

🌐 https://ai-crop-advisor-aa62.onrender.com

## 📖 Project Overview

AI Crop Advisor is an intelligent web application that assists farmers in selecting suitable crops based on agricultural conditions. Users provide information such as soil type, current crop, season, and water availability, and the application generates AI-powered recommendations with detailed explanations.

The project focuses on improving crop planning, supporting sustainable farming practices, and making agricultural guidance more accessible through an easy-to-use web interface.


## 🏠 Application Interface
<img width="1919" height="906" alt="ai-crop-advisor" src="https://github.com/user-attachments/assets/97eed183-849a-472d-9ad3-efe9c182f0a6" />

 ### 📊 Recommendation Results
<img width="1903" height="1017" alt="Screenshot 2026-07-07 144914" src="https://github.com/user-attachments/assets/58e650c4-b38b-457d-8730-7d8a338c8343" />

### 📊 Recommendation History Dashboard
<img width="1919" height="1016" alt="Screenshot 2026-07-07 145102" src="https://github.com/user-attachments/assets/f75fe1ba-a328-4bb0-8a6d-d61bd34cec4b" />

### 🌍 Multi-language Accessibility
<img width="1919" height="1018" alt="Screenshot 2026-07-07 145412" src="https://github.com/user-attachments/assets/31da3793-8654-4003-91ed-b3fd12a8a962" />

<img width="1919" height="1019" alt="Screenshot 2026-07-07 145449" src="https://github.com/user-attachments/assets/b167d868-930a-432f-a712-92c977709029" />

<img width="1917" height="1009" alt="Screenshot 2026-07-07 145538" src="https://github.com/user-attachments/assets/298c7ea7-ed3b-4867-92fa-8307d720c180" />

Supported Languages:
- English
- Telugu
- Hindi
- Kannada


## ✨ Features

- 🌱 AI-powered crop recommendations using the Groq API
- 🌾 Recommends suitable crops based on soil type, current crop, season, and water availability
- 🤖 Provides AI-generated explanations for each recommendation
- 🌍 Multi-language support for improved accessibility
- 📜 Stores recommendation history for future reference
- 📄 Download recommendation history as a PDF
- 🌙 Light and Dark theme support
- 📱 Responsive design for desktop and mobile devices
- 📲 Installable as a Progressive Web App (PWA)
- ☁️ Deployed on Render for online access


## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask
- Gunicorn

### Artificial Intelligence
- Groq API
- Large Language Models (LLMs)

### Database
- Supabase (PostgreSQL)

### PDF Generation
- ReportLab

### Deployment
- Render

###  Development Tools
- Git
- GitHub
- Visual Studio Code


## 🧑‍💻 Local Setup

### Prerequisites
- Python 3.9+
- Git
- A Groq API key
- A Supabase project (URL + API key)

### Clone the repository
```bash
git clone https://github.com/Divyaponnuru15/AI-Crop-Advisor.git
cd AI-Crop-Advisor
```

### Backend Setup

**1. Create a virtual environment**
```bash
python -m venv venv
```

**2. Activate the virtual environment**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root**
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

**5. Start the Flask server**
```bash
python app.py
```

**6. Open the app**
```
http://127.0.0.1:5000
```

