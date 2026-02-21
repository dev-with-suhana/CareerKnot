import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
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

# --- SIMPLE RESUME CHECK FUNCTION ---
def analyze_resume_basic(uploaded_file):

    file_size = uploaded_file.size / 1024  # in KB

    strength = "Weak"
    if file_size > 200:
        strength = "Average"
    if file_size > 500:
        strength = "Strong"

    return file_size, strength

# --- STUDENT PORTAL ---
def student_view():
    with st.sidebar:
        choice = option_menu(
            "Student Panel",
            ["Dashboard", "My Profile"],
            icons=["grid", "person"]
        )
        if st.button("Logout"):
            logout()

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
                size, strength = analyze_resume_basic(uploaded_pdf)

            st.success("Resume analyzed successfully ✅")

            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.write(f"**File Size:** {round(size,2)} KB")
            st.write(f"**Profile Strength:** {strength}")
            st.markdown("</div>", unsafe_allow_html=True)

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
