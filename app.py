import streamlit as st
from streamlit_option_menu import option_menu
from pymongo import MongoClient
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CareerKnot AI", page_icon="🔗", layout="wide")

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
    st.title("🔗 CareerKnot – AI Networking Platform")
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

    st.title("🎓 Student Dashboard")

    if choice == "Dashboard":
        skills = st.text_input("Your Skills (comma separated)", student.get("skills",""))
        interest = st.text_input("Career Interest", student.get("career_interest",""))
        if st.button("Update Profile"):
            students_col.update_one({"email":student["email"]},
                                    {"$set":{"skills":skills,"career_interest":interest}})
            st.success("Profile Updated")

    elif choice == "AI Mentor Match":
        mentors = list(mentors_col.find())
        matches = match_mentors(student, mentors)
        for mentor, score in matches:
            st.write(f"👨‍🏫 {mentor['name']} | Match Score: {round(score*100,2)}%")
            if st.button(f"Request {mentor['email']}"):
                requests_col.insert_one({"student_email": student["email"],
                                         "mentor_email": mentor["email"],
                                         "status": "Pending"})
                st.success("Request Sent")

    elif choice == "My Requests":
        reqs = requests_col.find({"student_email": student["email"]})
        for r in reqs:
            st.write("Mentor:", r["mentor_email"], "| Status:", r["status"])

    elif choice == "Career Roadmap":
        roadmap = career_roadmap(student.get("skills",""))
        for step in roadmap:
            st.write("✔", step)

    elif choice == "Internships":
        for job in internships_col.find():
            st.write("💼", job.get("title"), "|", job.get("company"))

    elif choice == "Industry Insights":
        for post in industry_col.find().sort("date",-1):
            st.subheader(post["title"])
            st.write(post["content"])
            st.write("Posted by:", post["mentor"])

    elif choice == "Chat":
        mentor_email = st.text_input("Mentor Email")
        message = st.chat_input("Type message")
        if message:
            chats_col.insert_one({"sender": student["email"], "receiver": mentor_email,
                                  "message": message, "timestamp": datetime.now()})
        messages = chats_col.find({"$or":[{"sender": student["email"], "receiver": mentor_email},
                                          {"sender": mentor_email, "receiver": student["email"]}]}).sort("timestamp",1)
        for m in messages:
            st.write(m["sender"], ":", m["message"])

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
        if reqs.count() == 0:
            st.info("No requests yet.")
        for r in reqs:
            st.write("Student:", r["student_email"], "| Status:", r["status"])
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
        st.write("Welcome Admin! Use the sidebar options to view or manage data.")

    elif choice == "Students":
        students = list(students_col.find())
        if len(students) == 0:
            st.info("No students yet.")
        for s in students:
            st.write("Name:", s['name'], "| Email:", s['email'], "| Skills:", s['skills'])

    elif choice == "Mentors":
        mentors = list(mentors_col.find())
        if len(mentors) == 0:
            st.info("No mentors yet.")
        for m in mentors:
            st.write("Name:", m['name'], "| Email:", m['email'], "| Skills:", m['skills'], "| Industry:", m['industry'])

    elif choice == "Internships":
        jobs = list(internships_col.find())
        if len(jobs) == 0:
            st.info("No internships posted yet.")
        for job in jobs:
            st.write(job['title'], "|", job['company'], "| Posted by:", job['mentor'])

    elif choice == "Industry Posts":
        posts = list(industry_col.find().sort("date",-1))
        if len(posts) == 0:
            st.info("No posts yet.")
        for post in posts:
            st.write(post['title'], "|", post['content'], "| Posted by:", post['mentor'])

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
