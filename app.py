import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import re  # Added for robust JSON parsing

# 1. Page Config
st.set_page_config(page_title="Smart ATS: V2", page_icon="🎓", layout="wide")

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
    
    # A. Career Stage
    experience_level = st.selectbox(
        "Select Career Stage:",
        ["Fresher (0-2 Years)", "Mid-Level (3-5 Years)", "Senior (5+ Years)"],
        index=0
    )
    
    # B. Target Region
    target_region = st.selectbox(
        "Target Market:",
        ["India 🇮🇳", "USA 🇺🇸", "Europe 🇪🇺", "Global 🌏"],
        index=0
    )
    
    st.divider()
    st.info(f"✅ **Mode Active:** Analyzing for a **{experience_level}** role in **{target_region}**.")

st.title("🎓 Smart ATS: Resume Optimizer")
st.markdown(f"Optimize your resume for **{target_region}** standards.")

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
    # Logic for Regions
    region_instruction = ""
    if "India" in target_region:
        region_instruction = "Check for standard Indian resume formats. Focus heavily on technical skills, projects, and marks/CGPA (if Fresher)."
    elif "USA" in target_region:
        region_instruction = "Strictly check for NO PHOTOS and NO PERSONAL DETAILS (Age, Marital Status). Ensure strict reverse-chronological order and action verbs."
    elif "Europe" in target_region:
        region_instruction = "Check for Europass compatibility standards. Ensure language proficiency is explicitly mentioned."
        
    # Logic for Experience
    experience_instruction = ""
    if "Fresher" in experience_level:
        experience_instruction = "Since this is a Fresher, be lenient on work experience but strict on Projects, Internships, and Core Concepts (DSA, OOPs). Look for 'Potential'."
    elif "Senior" in experience_level:
        experience_instruction = "Since this is a Senior, ignore university grades. Focus strictly on 'Leadership', 'Revenue Impact', and 'System Design' skills."

    # The Prompt
    prompt = f"""
    Act as a strict Technical Recruiter for the **{target_region}** market, hiring for a **{experience_level}** role.
    
    RESUME: {resume_text}
    JOB DESCRIPTION: {jd_text}
    
    INSTRUCTIONS:
    1. Evaluate the resume match percentage based on the JD.
    2. {region_instruction}
    3. {experience_instruction}
    4. Provide the output in strict JSON format.

    JSON FORMAT:
    {{
        "match_percentage": 0,
        "missing_keywords": ["keyword1", "keyword2"],
        "profile_summary": "Summary of the candidate...",
        "actionable_tips": ["tip1", "tip2"],
        "interview_questions": ["Q1", "Q2", "Q3"]
    }}
    """
    
    # Using the specific Flash model which is most stable
    model = genai.GenerativeModel("gemini-1.5-flash") 
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
        with st.spinner(f"Analyzing for {target_region} Market..."):
            try:
                resume_text = input_pdf_text(uploaded_file)
                response_text = get_gemini_response(resume_text, jd_text)
                
                # --- NEW: Robust JSON Parsing ---
                # This fixes the crash if Gemini adds extra text before/after the JSON
                match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if match:
                    raw_text = match.group(0)
                    data = json.loads(raw_text)
                else:
                    st.error("AI output format error. Please try again.")
                    st.stop()
                
                # --- DASHBOARD ---
                st.divider()
                
                # Score & Keywords
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

                # --- NEW: Profile Summary ---
                st.divider()
                st.subheader("📝 Profile Summary")
                st.write(data.get("profile_summary", "No summary generated."))

                # Tips & Interview
                st.divider()
                c3, c4 = st.columns(2)
                
                with c3:
                    st.subheader("💡 Tips to Improve")
                    for tip in data.get("actionable_tips", []):
                        st.info(f"👉 {tip}")
                        
                with c4:
                    st.subheader("🎤 Predicted Interview Questions")
                    st.write("Based on this JD, be ready for these:")
                    for q in data.get("interview_questions", []):
                        st.markdown(f"<div class='interview-q'>{q}</div>", unsafe_allow_html=True)

                # --- NEW: Download Report ---
                report_text = f"""
SMART ATS REPORT
----------------
Match Score: {score}%
Profile Summary: {data.get('profile_summary')}
Missing Keywords: {', '.join(keywords)}

Actionable Tips:
{chr(10).join(['- ' + t for t in data.get('actionable_tips', [])])}

Interview Questions:
{chr(10).join(['- ' + q for q in data.get('interview_questions', [])])}
"""
                st.download_button(
                    label="📥 Download Full Report",
                    data=report_text,
                    file_name="ats_report.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please upload both Resume and JD.")
