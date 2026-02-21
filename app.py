import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="CareerKnot", page_icon="🔗", layout="wide")

# --- 2. MASSIVE NAVY BRANDING & CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Inter:wght@400;600&display=swap');
    
    .stApp { background-color: #f8faff; }

    .brand-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 5.5rem;
        background: linear-gradient(90deg, #001f3f, #0074D9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    
    .brand-subtitle {
        font-family: 'Inter', sans-serif;
        color: #444;
        font-size: 1.8rem;
        text-align: center;
        margin-top: -15px;
        margin-bottom: 3rem;
    }

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

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

def logout():
    st.session_state.logged_in = False
    st.rerun()

# --- 4. LANDING / LOGIN PAGE ---
def landing_page():
    st.markdown("<h1 class='brand-title'>CareerKnot</h1>", unsafe_allow_html=True)
    st.markdown("<p class='brand-subtitle'>Bridging Student Ambition and Industry Reality</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tabs = st.tabs(["🔐 Login", "📝 Register"])
        with tabs[0]:
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["Student", "Mentor", "Admin"])
            if st.button("Enter Portal", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.rerun()

# --- 5. STUDENT PORTAL ---
def student_view():
    with st.sidebar:
        st.markdown("## CareerKnot")
        choice = option_menu(None, 
                             ["Dashboard", "My Profile", "Find Mentors", "Mentorship Request", "Skill Gap", "Chat", "Career Roadmap", "Industry Insights", "Settings"], 
                             icons=["grid", "person", "search", "send", "bar-chart", "chat", "map", "journal", "gear"], 
                             default_index=0)
        if st.button("Logout"): logout()

    st.title(f"{choice}")

    if choice == "Dashboard":
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Mentors", "2")
        c2.metric("Skill Match", "82%")
        c3.metric("Goal Progress", "Step 3/5")
        st.markdown("<div class='custom-card'><h4>System Alert</h4><p>Your resume analysis is complete. You are a strong match for 'Frontend Engineer' roles.</p></div>", unsafe_allow_html=True)

    elif choice == "My Profile":
        st.subheader("Professional Profile")
        st.text_input("Full Name", "Aryan Sharma")
        st.text_area("Skills", "Python, React, AWS, MongoDB")
        st.file_uploader("Update Resume (for AI analysis)")
        st.info("Keep your profile updated to get the best mentorship recommendations!")

    elif choice == "Find Mentors":
        st.subheader("Expert Network")
        st.text_input("Search experts by skill (e.g. Java, AI, Finance)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='custom-card'><b>Dr. Neha Verma</b><br>AI Lead @ Google<br><button>Request Mentorship</button></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='custom-card'><b>James Carter</b><br>Product Manager @ Amazon<br><button>Request Mentorship</button></div>", unsafe_allow_html=True)

    elif choice == "Mentorship Request":
        st.subheader("Submit a Mentorship Request")
        with st.form("request_form"):
            student_name = st.text_input("Your Name")
            topic = st.text_input("Topic / Area")
            details = st.text_area("Details / Description")
            submit_request = st.form_submit_button("Submit Request")
            if submit_request:
                st.success(f"Request submitted for {topic} by {student_name}")
        st.warning("Pending requests will appear here once mentors respond.")

    elif choice == "Skill Gap":
        st.subheader("Industry Readiness Gap")
        st.write("Target Role: **Data Scientist**")
        st.progress(90, text="Math & Stats (Strong)")
        st.progress(40, text="Big Data Tools (Gap Found)")
        st.progress(70, text="Python Programming (Good)")
        st.info("Recommendation: Connect with a Mentor to discuss Hadoop and Spark.")

    elif choice == "Career Roadmap":
        st.markdown("### Your Career Roadmap")
        roadmap_data = pd.DataFrame({
            "Stage": ["Foundation", "Specialization", "Industry Bridge"],
            "Progress": [100, 60, 20]
        })
        fig = px.timeline(roadmap_data, x_start=[0,100,160], x_end=[100,160,180], y="Stage", color="Stage")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        st.info("Tip: Complete each stage to unlock new mentorship opportunities.")

    elif choice == "Chat":
        st.write("Chat with: **Dr. Neha Verma**")
        st.chat_input("Type your message here...")
        st.markdown("Previous messages will appear here once conversation starts.")

    elif choice == "Industry Insights":
        st.subheader("Industry Comparison")
        data = pd.DataFrame({
            "Sector": ["Tech", "Finance", "Healthcare", "Education"],
            "Average Salary": [85000, 75000, 65000, 55000],
            "Job Growth": [12, 8, 10, 5]
        })
        fig = px.bar(data, x="Sector", y=["Average Salary", "Job Growth"], barmode="group", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
        st.info("Compare sectors to find the best fit for your skills.")

# --- 6. MENTOR PORTAL ---
def mentor_view():
    with st.sidebar:
        st.markdown("## CareerKnot")
        choice = option_menu(None, ["Dashboard", "Profile", "Requests", "Chat", "Settings"], 
            icons=["grid", "person-badge", "envelope", "chat", "gear"], default_index=0)
        if st.button("Logout"): logout()

    st.title(f"Mentor Portal: {choice}")

    if choice == "Dashboard":
        st.metric("Active Requests", "3")
        st.metric("Students Guided", "5")
        st.info("You are making an impact! Keep mentoring.")

    elif choice == "Profile":
        st.subheader("Mentor Profile")
        st.text_input("Full Name", "Dr. Neha Verma")
        st.text_area("Expertise", "AI, Machine Learning, Data Science")
        st.text_area("Bio", "Passionate about guiding students into tech careers.")
        st.file_uploader("Update Profile Photo")

    elif choice == "Requests":
        st.markdown("<div class='custom-card'><b>Student: Rahul V.</b><br>Topic: Backend Optimization<br><button>Accept</button> <button>Decline</button></div>", unsafe_allow_html=True)
        st.markdown("<div class='custom-card'><b>Student: Simran K.</b><br>Topic: AI Ethics<br><button>Accept</button> <button>Decline</button></div>", unsafe_allow_html=True)

    elif choice == "Chat":
        st.write("Chat with students: **Rahul V., Simran K.**")
        st.chat_input("Type your message here...")

    elif choice == "Settings":
        st.subheader("Settings")
        st.checkbox("Enable Notifications", value=True)
        st.checkbox("Show Availability to Students", value=True)
        st.info("Update your settings to manage how students can reach you.")

# --- 7. ADMIN PORTAL ---
def admin_view():
    with st.sidebar:
        st.markdown("## CareerKnot")
        choice = option_menu(None, ["Dashboard", "Student Data", "Mentor Data", "Settings"], 
            icons=["shield", "people", "briefcase", "gear"], default_index=0)
        if st.button("Logout"): logout()

    st.title(f"Admin portal: {choice}")

    if choice == "Dashboard":
        st.metric("Total Students", "120")
        st.metric("Total Mentors", "25")
        st.metric("Pending Requests", "8")
        st.info("Monitor platform activity here.")

    elif choice == "Student Data":
        st.table({"Student": ["Rahul", "Simran", "Aryan"], "Skill Match": ["85%", "70%", "92%"], "Requests Pending": [1, 0, 2]})

    elif choice == "Mentor Data":
        st.table({"Mentor": ["Dr. Neha Verma", "James Carter"], "Expertise": ["AI, ML", "Product Management"], "Active Requests": [2, 1]})

    elif choice == "Settings":
        st.subheader("Admin Settings")
        st.checkbox("Enable System Notifications", value=True)
        st.checkbox("Allow New Registrations", value=True)
        st.info("Configure platform-wide settings here.")

# --- MAIN ROUTER ---
if not st.session_state.logged_in:
    landing_page()
else:
    if st.session_state.user_role == "Student": student_view()
    elif st.session_state.user_role == "Mentor": mentor_view()
    elif st.session_state.user_role == "Admin": admin_view()
