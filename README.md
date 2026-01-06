# 🎓 Smart ATS: Resume Optimizer & Career Coach

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-ff4b4b)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini%202.0-orange)

**Smart ATS** is an AI-powered application designed to help job seekers beat Applicant Tracking Systems (ATS). It evaluates your resume against a specific Job Description (JD), identifies missing keywords, and acts as a personal career coach by providing **free study resources** and **interview preparation questions**.

## 🚀 Live Demo
**[Click here to Try the App Live!](https://smart-ats-resume-optimizer.streamlit.app/)** *(Note: If the link is not active yet, deploy it on Streamlit Cloud)*

## 🧠 Key Features

* **📊 Match Score Calculator:** Instantly get a percentage match score (0-100%) based on how well your resume aligns with the JD.
* **🔍 Keyword Gap Analysis:** Identifies critical technical skills and keywords missing from your profile (e.g., "You missed 'Excel' and 'A/B Testing'").
* **📚 Automated Study Plans:** Dynamically generates **"Click to Learn"** links for every missing skill, directing users to free tutorials and courses.
* **🎤 Interview Predictor:** Uses the JD to predict 5 specific technical and behavioral interview questions you are likely to be asked.
* **💡 Actionable Feedback:** Provides specific tips on how to rewrite bullet points to pass the ATS filters.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (for the interactive dashboard)
* **AI Engine:** [Google Gemini 1.5/2.0 Flash](https://ai.google.dev/) (via `google-generativeai`)
* **PDF Processing:** `PyPDF2` (to extract text from Resume PDFs)
* **Data Handling:** Python `json` parsing for structured outputs.

## 📸 Screenshots

*(Add a screenshot of your dashboard here later!)*

## ⚙️ Installation & Local Setup

Want to run this locally? Follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/VaishnaviGahoi/Smart-ATS-Resume-Optimizer.git](https://github.com/VaishnaviGahoi/Smart-ATS-Resume-Optimizer.git)
    cd Smart-ATS-Resume-Optimizer
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up API Key:**
    * Create a `.streamlit` folder in the root directory.
    * Create a `secrets.toml` file inside it.
    * Add your Google Gemini API key:
        ```toml
        GEMINI_API_KEY = "Your_API_Key_Here"
        ```

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features (e.g., Cover Letter generation, LinkedIn optimization), feel free to fork the repo and submit a Pull Request.

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---
*Built with ❤️ by Vaishnavi Gahoi*