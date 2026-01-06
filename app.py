import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json

# 1. Page Config
st.set_page_config(page_title="Smart ATS: Career Coach", page_icon="🎓", layout="wide")

# Custom CSS (FIXED COLORS)
st.markdown("""
<style>
    /* 1. Missing Keyword Tags (Dark Background + Gold Text) */
    .keyword-tag {
        display: inline-block;
        padding: 5px 10px;
        margin: 5px;
        background-color: #1e1e1e; /* Dark Grey */
        color: #ffb700; /* Gold/Yellow Text */
        border: 1px solid #ffb700;
        border-radius: 15px;
        font-weight: bold;
    }
    
    /* 2. Score Card */
    .score-card {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background-color: #262730; /* Matches Streamlit Dark Mode */
        border: 1px solid #41444e;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* 3. Interview Question Box (FIXED: Dark Background + White Text) */
    .interview-q {
        background-color: #0e1117; /* Very Dark Background */
        color: #ffffff; /* FORCE WHITE TEXT */
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 5px solid #00d4ff; /* Cyan Neon Accent */
        border: 1px solid #303030;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Smart ATS: Resume Optimizer & Coach")
st.markdown("Optimize your resume, get **study resources**, and prepare for the **interview**.")

# 2. Setup Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key not found.")

# 3. Text Extraction
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += page.extract_text()
    return text

# 4. The "Career Coach" Prompt
sys_instruction = """
You are a Career Coach & Technical Recruiter. 
Analyze the Resume against the Job Description (JD).

Output purely in this JSON format:
{
    "match_percentage": 0,
    "missing_keywords": ["keyword1", "keyword2"],
    "profile_summary": "...",
    "actionable_tips": ["tip1", "tip2"],
    "interview_questions": [
        "Question 1 based on JD requirements?",
        "Question 2 based on Resume gaps?",
        "Question 3 technical deep dive?"
    ]
}
"""

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=sys_instruction
)

# 5. UI Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job Description")
    jd_text = st.text_area("Paste JD here...", height=300)

with col2:
    st.subheader("2. Your Resume")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

# 6. Analysis Logic
if st.button("Analyze & Coach Me 🚀", type="primary"):
    if uploaded_file is not None and jd_text:
        with st.spinner("Analyzing profile & generating interview questions..."):
            try:
                # Text Processing
                resume_text = input_pdf_text(uploaded_file)
                prompt = f"RESUME: {resume_text}\n---\nJOB DESCRIPTION: {jd_text}"
                
                response = model.generate_content(prompt)
                
                # Parse JSON
                raw_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(raw_text)
                
                # --- DASHBOARD ---
                st.divider()
                
                # A. Score & Keywords
                c1, c2 = st.columns([1, 2])
                score = data.get("match_percentage", 0)
                
                # Color Logic
                if score >= 80: color = "#4caf50" # Green
                elif score >= 50: color = "#ff9800" # Orange
                else: color = "#f44336" # Red
                
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
                        # Display tags
                        tags_html = "".join([f"<span class='keyword-tag'>{k}</span>" for k in keywords])
                        st.markdown(tags_html, unsafe_allow_html=True)
                        
                        # Dynamic Study Links
                        with st.expander("📚 Click to Learn Missing Skills"):
                            st.write("We found free resources for your gaps:")
                            for k in keywords:
                                # Smart Google Search Link
                                link = f"https://www.google.com/search?q=free+course+tutorial+{k.replace(' ', '+')}"
                                st.markdown(f"👉 **[{k}]({link})** (Search Free Courses)")
                    else:
                        st.success("No critical gaps found!")

                # B. Interview Prep
                st.divider()
                c3, c4 = st.columns(2)
                
                with c3:
                    st.subheader("💡 How to Improve")
                    for tip in data.get("actionable_tips", []):
                        st.info(f"👉 {tip}")
                        
                with c4:
                    st.subheader("🎤 Predicted Interview Questions")
                    st.write("Based on this JD, be ready for these:")
                    for q in data.get("interview_questions", []):
                        # Use the new .interview-q class
                        st.markdown(f"<div class='interview-q'>{q}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
                st.write(response.text) # Fallback
    else:
        st.warning("Please upload both Resume and JD.")