import os
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from PyPDF2 import PdfReader
import docx

# ----------------------------
# Load API Key from secrets or environment variable
# ----------------------------
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key and "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]

if not groq_api_key:
    st.error("❌ GROQ_API_KEY not set. Please set it before running.")
    st.stop()

# ----------------------------
# Custom Styling (Dark Theme + White Inputs)
# ----------------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        font-family: 'Poppins', sans-serif;
        color: #f0f0f0;
    }
    .title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #00e5ff;
        margin-bottom: 25px;
    }
    .subtitle {
        text-align: center;
        font-size: 20px;
        font-style: italic;
        color: #ffcc70;
        margin-bottom: 30px;
    }
    .section {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }
    /* ✅ All text areas white */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
        border-radius: 12px;
        padding: 10px;
        font-size: 16px;
    }
    /* White background for email output */
    .email-box {
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ccc;
        font-family: 'Arial', sans-serif;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        margin-top: 15px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #0077b6, #023e8a);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 28px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #023e8a, #0077b6);
        transform: scale(1.05);
    }
    .sidebar-title {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #FFD700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Initialize Groq LLM
# ----------------------------
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

# ----------------------------
# App Title + Tagline
# ----------------------------
st.markdown(
    """
    <div style="text-align: center; padding: 15px;">
        <h1 style="color:#FF4B4B; font-size:42px; font-weight:bold;">
            ✉️ AI Cold Email Generator
        </h1>
        <h3 style="color:#1E90FF; font-size:22px; font-style:italic;">
            🚀 Crafting personalized emails that get noticed
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Sidebar Branding
# ----------------------------
st.sidebar.markdown("### 🌟 **Zubair Satti's Opportunity Hub**", unsafe_allow_html=True)
st.sidebar.markdown("💼 Your personal AI assistant for professional outreach")

creativity = st.sidebar.slider("✨ Creativity", 0, 100, 50)
personalization = st.sidebar.slider("🤝 Personalization", 0, 100, 70)

st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by **Zubair Satti**")

# ----------------------------
# Resume Upload Section
# ----------------------------
portfolio = ""
with st.container():
    st.markdown('<div class="section">📂 <b>Upload Resume or Paste Text</b></div>', unsafe_allow_html=True)
    uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded_resume:
        if uploaded_resume.type == "application/pdf":
            reader = PdfReader(uploaded_resume)
            extracted_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif uploaded_resume.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_resume)
            extracted_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            extracted_text = ""
        portfolio = extracted_text
        st.success("✅ Resume text extracted successfully!")

    # ✅ Always show text area as alternative
    manual_portfolio = st.text_area("✍️ Or paste your portfolio / resume text here:")
    if manual_portfolio.strip():
        portfolio = manual_portfolio


# ----------------------------
# Job Description & Portfolio
# ----------------------------
with st.container():
    st.markdown('<div class="section">📄 <b>Job Information</b></div>', unsafe_allow_html=True)
    job_description = st.text_area("📌 Paste Job Description here:")
    extra_skills = st.text_area("💡 Add Extra Skills / Highlights (Optional):")
    if not portfolio:
        portfolio = st.text_area("📂 Paste Portfolio / Resume here:")

# ----------------------------
# Customization Section
# ----------------------------
with st.container():
    st.markdown('<div class="section">⚙️ <b>Email Customization</b></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        tone = st.radio("🎭 Choose the tone:", ["Professional", "Friendly", "Persuasive", "Concise"], index=0)
    with col2:
        email_format = st.radio("📑 Choose Email Format:", ["Formal Letter", "Short Note"], index=0)

# ----------------------------
# Session State for History
# ----------------------------
if "email_history" not in st.session_state:
    st.session_state.email_history = []

# ----------------------------
# Generate Email
# ----------------------------
if st.button("🚀 Generate Email"):
    if job_description and portfolio:
        combined_portfolio = portfolio + "\n\nExtra Skills:\n" + extra_skills

        prompt = PromptTemplate(
            input_variables=["job_description", "portfolio", "tone", "creativity", "personalization", "email_format"],
            template=(
                "You are an assistant drafting a {tone} cold email in {email_format} style.\n"
                "Creativity Level: {creativity}/100.\n"
                "Personalization Level: {personalization}/100.\n\n"
                "Job Description:\n{job_description}\n\n"
                "Portfolio/Resume & Extra Skills:\n{portfolio}\n\n"
                "Write a cold email tailored for this job."
            ),
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({
            "job_description": job_description,
            "portfolio": combined_portfolio,
            "tone": tone,
            "creativity": creativity,
            "personalization": personalization,
            "email_format": email_format
        })

        # Subject Line
        subject_prompt = PromptTemplate(
            input_variables=["job_description"],
            template="Write a catchy subject line for a cold email based on this job description:\n{job_description}"
        )
        subject_chain = LLMChain(llm=llm, prompt=subject_prompt)
        subject_line = subject_chain.run({"job_description": job_description})

        # Output
        st.markdown('<div class="section">📌 <b>Suggested Subject Line</b></div>', unsafe_allow_html=True)
        st.success(subject_line)

        st.markdown('<div class="section">✉️ <b>Generated Cold Email</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="email-box">{response}</div>', unsafe_allow_html=True)

        # Download
        email_text = f"Subject: {subject_line}\n\n{response}"
        st.download_button("📥 Download Email as TXT", email_text, "cold_email.txt")

        # Save History
        st.session_state.email_history.append({"subject": subject_line, "body": response})
    else:
        st.warning("⚠ Please provide both Job Description and Portfolio.")

# ----------------------------
# Email History
# ----------------------------
if st.session_state.email_history:
    st.markdown('<div class="section">📜 <b>Email History</b></div>', unsafe_allow_html=True)
    for idx, email in enumerate(st.session_state.email_history):
        with st.expander(f"📧 Email {idx+1}: {email['subject']}"):
            st.write(email['body'])
