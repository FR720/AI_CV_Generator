# AI CV Generator

Generate professional, tailored CVs using **Google Gemini** AI. A Streamlit web app that turns your details + target job into a polished, ready-to-download CV.

## ✨ Features

- AI-generated CV content via **Google Gemini 1.5 Pro**
- Clean **Streamlit** web interface
- **PDF export** (ReportLab / FPDF)
- API key validation before generating
- CrewAI-based generation workflow

## 🚀 Getting started

```bash
# 1. Clone
git clone https://github.com/FR720/AI_CV_Generator.git
cd AI_CV_Generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Google AI key
#    (create one at https://aistudio.google.com)
export GOOGLE_API_KEY=your_key_here

# 4. Run
streamlit run app.py
```

## 🛠️ Tech stack

Python · Streamlit · Google Generative AI · CrewAI · ReportLab

## 📄 License

MIT
