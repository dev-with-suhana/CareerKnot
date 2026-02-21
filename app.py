import streamlit as st
from streamlit_option_menu import option_menu
from pymongo import MongoClient
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CareerKnot AI", page_icon="🔗", layout="wide")

# ---------------- CUSTOM LIGHT THEME ----------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto+Slab:wght@700&display=swap');

    /* APP BACKGROUND */
    .stApp { 
        background-color: #fefefe;
        color: #111;
        font-family: 'Inter', sans-serif;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #f0f0f0 !important;
        color: #111 !important;
    }
    [data-testid="stSidebar"] .css-1d391kg {color: #111 !important;}

    /* TITLES */
    h1, h2, h3, h4 {
        font-family: 'Roboto Slab', serif;
        color: #111;
    }

    /* CUSTOM CARDS */
    .custom-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["careerknot"]

students_col = db["students"]
mentors_col = db["mentors"]
admins_col = db["admins"]
requests_col = db["requests"]
chats_col = db["chats"]
internships_col = db["internships"]
industry_col = db["industry_posts"]

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def logout():
    st.session_state.clear()
    st.rerun()

# ---------------- AI MATCHING FUNCTION ----------------
def match_mentors(student, mentors):
    mentor_profiles = [m.get("skills","") + " " + m.get("industry","") for m in mentors]
    student_profile = student.get("skills","") + " " + student.get("career_interest","")
    docs = mentor_profiles + [student_profile]
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(docs)
    scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
    ranked = sorted(zip(mentors, scores), key=lambda x: x[1], reverse=True)
    return ranked[:5]

# ---------------- CAREER ROADMAP ----------------
def career_roadmap(skills):
    roadmap = []
    if "python" in skills.lower():
        roadmap += ["Learn DSA", "Build Backend Projects", "Practice APIs", "Apply Backend Jobs"]
    if "machine learning" in skills.lower():
        roadmap += ["Master Statistics", "Build ML Projects", "Deploy Models", "Apply ML Roles"]
    if "web" in skills.lower():
        roadmap += ["Learn React/Node", "Build Full Stack Projects", "Deploy Website"]
    return roadmap

# ---------------- AUTH ----------------
def register_user(name, email, password, role):
    data = {"name": name, "email": email, "password": password,
            "skills": "", "career_interest": "", "industry": ""}
    if role == "Student":
        students_col.insert_one(data)
    elif role == "Mentor":
        mentors_col.insert_one(data)
    else:
        admins_col.insert_one(data)

def login_user(email, password, role):
    collection = students_col if role == "Student" else mentors_col if role == "Mentor" else admins_col
    return collection.find_one({"email": email, "password": password})

# ---------------- LANDING PAGE ----------------
def landing_page():
    st.markdown("<h1 style='font-family:Roboto Slab'>🔗 CareerKnot – AI Networking Platform</h1>", unsafe_allow_html=True)
    st.subheader("Connecting Students with Industry Professionals")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Student", "Mentor", "Admin"])

        if st.button("Login"):
            user = login_user(email, password, role)
            if user:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Invalid Credentials")

    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        role = st.selectbox("Role", ["Student", "Mentor", "Admin"], key="reg_role")

        if st.button("Register"):
            register_user(name, email, password, role)
            st.success("Registration Successful!")

# ---------------- STUDENT PORTAL ----------------
def student_portal():
    student = students_col.find_one({"email": st.session_state.user_email})

    with st.sidebar:
        choice = option_menu("Student Menu",
                             ["Dashboard","AI Mentor Match","My Requests",
                              "Career Roadmap","Internships",
                              "Industry Insights","Chat","Logout"])

    if choice == "Logout":
        logout()

    st.title(f"🎓 Student - {choice}")

    # Dashboard / Profile
    if choice == "Dashboard":
        skills = st.text_input("Your Skills (comma separated)", student.get("skills",""))
        interest = st.text_input("Career Interest", student.get("career_interest",""))
        if st.button("Update Profile"):
            students_col.update_one({"email":student["email"]},
                                    {"$set":{"skills":skills,"career_interest":interest}})
            st.success("Profile Updated")

    # AI Mentor Match
    elif choice == "AI Mentor Match":
        mentors = list(mentors_col.find())
        matches = match_mentors(student, mentors)
        for mentor, score in matches:
            st.markdown(f"<div class='custom-card'>👨‍🏫 {mentor['name']} | Match Score: {round(score*100,2)}%</div>", unsafe_allow_html=True)
            if st.button(f"Request {mentor['email']}"):
                requests_col.insert_one({"student_email": student["email"],
                                         "mentor_email": mentor["email"],
                                         "status": "Pending"})
                st.success("Request Sent")

    elif choice == "My Requests":
        reqs = requests_col.find({"student_email": student["email"]})
        for r in reqs:
            st.markdown(f"<div class='custom-card'>Mentor: {r['mentor_email']} | Status: {r['status']}</div>", unsafe_allow_html=True)

    elif choice == "Career Roadmap":
        roadmap = career_roadmap(student.get("skills",""))
        for step in roadmap:
            st.markdown(f"<div class='custom-card'>✔ {step}</div>", unsafe_allow_html=True)

    elif choice == "Internships":
        for job in internships_col.find():
            st.markdown(f"<div class='custom-card'>💼 {job.get('title')} | {job.get('company')}</div>", unsafe_allow_html=True)

    elif choice == "Industry Insights":
        for post in industry_col.find().sort("date",-1):
            st.markdown(f"<div class='custom-card'><h4>{post['title']}</h4>{post['content']}<br>Posted by: {post['mentor']}</div>", unsafe_allow_html=True)

    elif choice == "Chat":
        mentor_email = st.text_input("Mentor Email")
        message = st.chat_input("Type message")
        if message:
            chats_col.insert_one({"sender": student["email"], "receiver": mentor_email,
                                  "message": message, "timestamp": datetime.now()})
        messages = chats_col.find({"$or":[{"sender": student["email"], "receiver": mentor_email},
                                          {"sender": mentor_email, "receiver": student["email"]}]}).sort("timestamp",1)
        for m in messages:
            st.markdown(f"<div class='custom-card'>{m['sender']}: {m['message']}</div>", unsafe_allow_html=True)

# ---------------- MENTOR PORTAL ----------------
def mentor_portal():
    mentor = mentors_col.find_one({"email": st.session_state.user_email})

    with st.sidebar:
        choice = option_menu("Mentor Menu",
                             ["Dashboard","Requests","Post Internship","Post Industry Insight","Logout"])

    if choice == "Logout":
        logout()

    st.title(f"👨‍🏫 Mentor - {choice}")

    if choice == "Dashboard":
        skills = st.text_input("Your Skills", mentor.get("skills",""))
        industry = st.text_input("Industry", mentor.get("industry",""))
        if st.button("Update Profile"):
            mentors_col.update_one({"email":mentor["email"]},
                                   {"$set":{"skills":skills,"industry":industry}})
            st.success("Profile Updated")

    elif choice == "Requests":
        reqs = requests_col.find({"mentor_email": mentor["email"]})
        for r in reqs:
            st.markdown(f"<div class='custom-card'>Student: {r['student_email']} | Status: {r['status']}</div>", unsafe_allow_html=True)
            if st.button(f"Accept {r['_id']}"):
                requests_col.update_one({"_id":r["_id"]},{"$set":{"status":"Accepted"}})
                st.success("Accepted")

    elif choice == "Post Internship":
        title = st.text_input("Job Title")
        company = st.text_input("Company Name")
        if st.button("Post Internship"):
            internships_col.insert_one({"title":title,"company":company,"mentor":mentor["email"],"date":datetime.now()})
            st.success("Internship Posted")

    elif choice == "Post Industry Insight":
        title = st.text_input("Post Title")
        content = st.text_area("Content")
        if st.button("Publish"):
            industry_col.insert_one({"title":title,"content":content,"mentor":mentor["email"],"date":datetime.now()})
            st.success("Posted Successfully")

# ---------------- ADMIN PORTAL ----------------
def admin_portal():
    admin = admins_col.find_one({"email": st.session_state.user_email})

    with st.sidebar:
        choice = option_menu("Admin Menu",
                             ["Dashboard","Students","Mentors","Internships","Industry Posts","Logout"])

    if choice == "Logout":
        logout()

    st.title(f"🛠 Admin - {choice}")

    if choice == "Dashboard":
        st.markdown("<div class='custom-card'>Welcome Admin! Use the sidebar to manage users and posts.</div>", unsafe_allow_html=True)

    elif choice == "Students":
        students = list(students_col.find())
        for s in students:
            st.markdown(f"<div class='custom-card'>Name: {s['name']} | Email: {s['email']} | Skills: {s['skills']}</div>", unsafe_allow_html=True)

    elif choice == "Mentors":
        mentors = list(mentors_col.find())
        for m in mentors:
            st.markdown(f"<div class='custom-card'>Name: {m['name']} | Email: {m['email']} | Skills: {m['skills']} | Industry: {m['industry']}</div>", unsafe_allow_html=True)

    elif choice == "Internships":
        for job in internships_col.find():
            st.markdown(f"<div class='custom-card'>{job['title']} | {job['company']} | Posted by: {job['mentor']}</div>", unsafe_allow_html=True)

    elif choice == "Industry Posts":
        for post in industry_col.find().sort("date",-1):
            st.markdown(f"<div class='custom-card'>{post['title']} | {post['content']} | Posted by: {post['mentor']}</div>", unsafe_allow_html=True)

# ---------------- MAIN ----------------
if not st.session_state.logged_in:
    landing_page()
else:
    if st.session_state.role == "Student":
        student_portal()
    elif st.session_state.role == "Mentor":
        mentor_portal()
    elif st.session_state.role == "Admin":
        admin_portal()
