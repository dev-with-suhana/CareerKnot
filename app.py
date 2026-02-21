import streamlit as st
from streamlit_option_menu import option_menu
from pymongo import MongoClient
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CareerKnot", page_icon="🔗", layout="wide")

# ------------------ DATABASE CONNECTION ------------------
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["careerknot"]

students_col = db["students"]
mentors_col = db["mentors"]
admins_col = db["admins"]
requests_col = db["requests"]
chats_col = db["chats"]

# ------------------ SESSION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def logout():
    st.session_state.clear()
    st.rerun()

# ------------------ AUTH SYSTEM ------------------
def register_user(name, email, password, role):
    data = {"name": name, "email": email, "password": password}

    if role == "Student":
        students_col.insert_one(data)
    elif role == "Mentor":
        mentors_col.insert_one(data)
    else:
        admins_col.insert_one(data)

def login_user(email, password, role):
    collection = students_col if role == "Student" else mentors_col if role == "Mentor" else admins_col
    return collection.find_one({"email": email, "password": password})

# ------------------ LANDING PAGE ------------------
def landing_page():
    st.title("🔗 CareerKnot")
    st.subheader("Bridging Student Ambition and Industry Reality")

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
                st.success("Login Successful!")
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

# ------------------ STUDENT PORTAL ------------------
def student_portal():
    with st.sidebar:
        choice = option_menu("Student Menu",
                             ["Dashboard", "Find Mentors", "My Requests", "Chat", "Logout"])

    if choice == "Logout":
        logout()

    st.title("🎓 Student Portal")

    if choice == "Dashboard":
        st.write("Welcome,", st.session_state.user_email)

    elif choice == "Find Mentors":
        mentors = list(mentors_col.find())
        for mentor in mentors:
            st.write("👨‍🏫", mentor["name"], "-", mentor["email"])
            if st.button(f"Request {mentor['email']}"):
                requests_col.insert_one({
                    "student_email": st.session_state.user_email,
                    "mentor_email": mentor["email"],
                    "status": "Pending"
                })
                st.success("Request Sent!")

    elif choice == "My Requests":
        my_requests = requests_col.find({"student_email": st.session_state.user_email})
        for req in my_requests:
            st.write("Mentor:", req["mentor_email"], "| Status:", req["status"])

    elif choice == "Chat":
        mentor_email = st.text_input("Mentor Email")

        message = st.chat_input("Type message")
        if message:
            chats_col.insert_one({
                "sender": st.session_state.user_email,
                "receiver": mentor_email,
                "message": message,
                "timestamp": datetime.now()
            })

        messages = chats_col.find({
            "$or": [
                {"sender": st.session_state.user_email, "receiver": mentor_email},
                {"sender": mentor_email, "receiver": st.session_state.user_email}
            ]
        }).sort("timestamp", 1)

        for msg in messages:
            st.write(msg["sender"], ":", msg["message"])

# ------------------ MAIN ------------------
if not st.session_state.logged_in:
    landing_page()
else:
    if st.session_state.role == "Student":
        student_portal()