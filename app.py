import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from PyPDF2 import PdfReader
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="CareerKnot", page_icon="🔗", layout="wide")

# --- CSS ---
st.markdown("""
<style>
.stApp { background-color: #f8faff; }
[data-testid="stSidebar"] { background-color: #001f3f !important; }
[data-testid="stSidebar"] * { color: white !important; }

.custom-card {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    border-left: 8px solid #001f3f;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

def logout():
    st.session_state.logged_in = False
    st.rerun()

# --- LOGIN ---
def landing_page():
    st.title("CareerKnot 🔗")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Student", "Mentor", "Admin"])
    if st.button("Enter Portal"):
        st.session_state.logged_in = True
        st.session_state.user_role = role
        st.rerun()

# --- PDF ANALYSIS FUNCTION ---
def analyze_resume(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    words = text.split()
    word_count = len(words)

    skills_db = [
        "python","java","react","aws","mongodb","sql","machine learning",
        "data science","html","css","javascript"
    ]

    found_skills = []
    for skill in skills_db:
        if re.search(rf"\b{skill}\b", text.lower()):
            found_skills.append(skill.title())

    strength = "Weak"
    if word_count > 300:
        strength = "Average"
    if word_count > 600:
        strength = "Strong"

    return text, word_count, found_skills, strength

# --- STUDENT PORTAL ---
def student_view():
    with st.sidebar:
        choice = option_menu(
            "Student Panel",
            ["Dashboard", "My Profile"],
            icons=["grid", "person"]
        )
        if st.button("Logout"): logout()

    st.title(choice)

    if choice == "Dashboard":
        st.metric("Profile Strength", "Good")
        st.info("Upload resume in My Profile for AI analysis")

    elif choice == "My Profile":
        st.subheader("Professional Profile")

        st.text_input("Full Name", "Aryan Sharma")
        st.text_area("Skills", "Python, React, AWS")

        uploaded_pdf = st.file_uploader(
            "Upload Resume (PDF only)",
            type=["pdf"]
        )

        if uploaded_pdf:
            with st.spinner("Analyzing resume..."):
                text, words, skills, strength = analyze_resume(uploaded_pdf)

            st.success("Resume analyzed successfully ✅")

            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.write(f"**Total Words:** {words}")
            st.write(f"**Profile Strength:** {strength}")

            if skills:
                st.write("**Detected Skills:**")
                st.write(", ".join(skills))
            else:
                st.warning("No recognizable skills found")

            st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("📄 View Resume Text"):
                st.write(text)

# --- MENTOR ---
def mentor_view():
    st.title("Mentor Portal")
    st.info("Mentor features coming soon")

# --- ADMIN ---
def admin_view():
    st.title("Admin Portal")
    st.info("Admin dashboard coming soon")

# --- ROUTER ---
if not st.session_state.logged_in:
    landing_page()
else:
    if st.session_state.user_role == "Student":
        student_view()
    elif st.session_state.user_role == "Mentor":
        mentor_view()
    else:
        admin_view()
