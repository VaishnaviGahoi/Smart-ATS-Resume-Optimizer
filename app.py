import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import re

# 1. Page Config
st.set_page_config(page_title="Smart ATS: Pro", page_icon="🎓", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .keyword-tag {
        display: inline-block;
        padding: 5px 10px;
        margin: 5px;
        background-color: #1e1e1e;
        color: #ffb700;
        border: 1px solid #ffb700;
        border-radius: 15px;
        font-weight: bold;
    }
    .score-card {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background-color: #262730;
        border: 1px solid #41444e;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .interview-q {
        background-color: #0e1117;
        color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 5px solid #00d4ff;
        border: 1px solid #303030;
    }
</style>
""", unsafe_allow_html=True)

# 2. Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Smart Configuration")
    
    # Filters
    experience_level = st.selectbox("Career Stage", ["Fresher", "Mid-Level", "Senior"], index=0)
    target_region = st.selectbox("Target Market", ["India 🇮🇳", "USA 🇺🇸", "Europe 🇪🇺", "Global 🌏"], index=0)
    target_company = st.selectbox("Target Company", ["FAANG / Big Tech", "Startup / Product", "Service / Consulting"], index=0)
    
    st.divider()
    st.info(f"✅ **Mode Active:** Auditing for a **{target_company}** role in **{target_region}**.")

st.title("🎓 Smart ATS: Resume Optimizer")
st.markdown(f"Optimize your resume for **{target_company}** standards.")

# 3. Setup Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key not found. Please add it to secrets.toml")

# 4. Text Extraction
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += page.extract_text()
    return text

# 5. Dynamic Prompt Logic
def get_gemini_response(resume_text, jd_text):
    
    # Logic for Company
    company_instruction = ""
    if "FAANG" in target_company:
        company_instruction = "Benchmark against **Google/Meta standards**. Look for: 'Scale', 'Impact', 'Data Structures'. Penalize generic descriptions."
    elif "Startup" in target_company:
        company_instruction = "Benchmark against **High-Growth Startups**. Look for: 'Speed', 'Ownership', 'Full Stack' mentality."
    elif "Service" in target_company:
        company_instruction = "Benchmark against **Service/Consulting giants**. Look for: 'Client Handling', 'Tools Proficiency', 'Certifications'."

    # Logic for Experience
    experience_instruction = ""
    if "Fresher" in experience_level:
        experience_instruction = "Strictly focus on Projects, Internships, and Core Concepts (DSA, OOPs). Ignore lack of full-time experience."
    elif "Senior" in experience_level:
        experience_instruction = "Focus strictly on 'Leadership', 'Revenue Impact', and 'System Design'."

    # Prompt
    prompt = f"""
    Act as a strict Technical Recruiter for a **{target_company}** in **{target_region}**, hiring for a **{experience_level}** role.
    
    RESUME: {resume_text}
    JOB DESCRIPTION: {jd_text}
    
    INSTRUCTIONS:
    1. Evaluate the resume match percentage based on the JD.
    2. {company_instruction}
    3. {experience_instruction}
    4. Provide the output in strict JSON format.

    JSON FORMAT:
    {{
        "match_percentage": 0,
        "missing_keywords": ["keyword1", "keyword2"],
        "profile_summary": "Summary...",
        "actionable_tips": ["tip1", "tip2"],
        "interview_questions": ["Q1", "Q2"]
    }}
    """
    
    # Using the stable Flash model
    model = genai.GenerativeModel("gemini-flash-latest") 
    response = model.generate_content(prompt)
    return response.text

# 6. UI Layout & Analysis
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job Description")
    jd_text = st.text_area("Paste JD here...", height=300)

with col2:
    st.subheader("2. Your Resume")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if st.button("Analyze & Coach Me 🚀", type="primary"):
    if uploaded_file is not None and jd_text:
        with st.spinner(f"Auditing against {target_company} Standards..."):
            try:
                resume_text = input_pdf_text(uploaded_file)
                response_text = get_gemini_response(resume_text, jd_text)
                
                # Robust Parsing
                match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if match:
                    raw_text = match.group(0)
                    data = json.loads(raw_text)
                else:
                    st.error("AI output format error. Please try again.")
                    st.stop()
                
                # --- DASHBOARD ---
                st.divider()
                
                # Score
                c1, c2 = st.columns([1, 2])
                score = data.get("match_percentage", 0)
                if score >= 80: color = "#4caf50"
                elif score >= 50: color = "#ff9800"
                else: color = "#f44336"
                
                with c1:
                    st.markdown(f"""
                    <div class="score-card">
                        <h2 style='color: {color}; font-size: 40px; margin:0;'>{score}%</h2>
                        <p style='color: #ffffff;'>Match Score</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with c2:
                    st.subheader("⚠️ Missing Skills")
                    keywords = data.get("missing_keywords", [])
                    if keywords:
                        tags_html = "".join([f"<span class='keyword-tag'>{k}</span>" for k in keywords])
                        st.markdown(tags_html, unsafe_allow_html=True)
                        with st.expander("📚 Click to Learn Missing Skills"):
                            for k in keywords:
                                link = f"https://www.google.com/search?q=free+course+tutorial+{k.replace(' ', '+')}"
                                st.markdown(f"👉 **[{k}]({link})**")
                    else:
                        st.success("No critical gaps found!")

                # Profile Summary
                st.divider()
                st.subheader("📝 Profile Summary")
                st.write(data.get("profile_summary", "No summary generated."))

                # Tips
                st.divider()
                st.subheader("💡 Tips to Improve")
                for tip in data.get("actionable_tips", []):
                    st.info(f"👉 {tip}")
                        
                # Interview Qs
                st.divider()
                st.subheader("🎤 Predicted Interview Questions")
                for q in data.get("interview_questions", []):
                    st.markdown(f"<div class='interview-q'>{q}</div>", unsafe_allow_html=True)

                # Download Report
                report_text = f"SMART ATS REPORT\nScore: {score}%\n\n{data.get('profile_summary')}"
                st.download_button("📥 Download Report", report_text, "report.txt")

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please upload both Resume and JD.")
