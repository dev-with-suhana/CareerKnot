# --- 7. ADMIN PORTAL (Enhanced) ---
import numpy as np
import plotly.express as px

def admin_view():
    with st.sidebar:
        st.markdown("## CareerKnot Admin")
        choice = option_menu(None, ["Dashboard", "Student Portal", "Mentor Portal", "Logout"], 
                             icons=["grid", "people", "briefcase", "box-arrow-right"], default_index=0)
        
        # Logout button
        if choice == "Logout" or st.button("Logout"):
            logout()
            return

    if choice == "Dashboard":
        st.title("Admin Dashboard")

        # Random data for students & mentors
        num_students = 50
        num_mentors = 10
        student_growth = np.random.randint(1, 10, size=6).cumsum()
        mentor_growth = np.random.randint(0, 3, size=6).cumsum()
        months = pd.date_range(end=pd.Timestamp.today(), periods=6, freq='M').strftime("%b %Y")

        # Metrics
        c1, c2 = st.columns(2)
        c1.metric("Total Students", num_students)
        c2.metric("Total Mentors", num_mentors)

        # Growth charts
        growth_df = pd.DataFrame({
            "Month": months,
            "Student Growth": student_growth,
            "Mentor Growth": mentor_growth
        })

        fig = px.line(growth_df, x="Month", y=["Student Growth", "Mentor Growth"], 
                      markers=True, title="Monthly Growth")
        st.plotly_chart(fig, use_container_width=True)

        # Pie chart example
        pie_df = pd.DataFrame({
            "Category": ["Tech", "Finance", "Healthcare", "Education"],
            "Students": np.random.randint(5, 20, size=4)
        })
        fig2 = px.pie(pie_df, names='Category', values='Students', title="Student Distribution by Sector")
        st.plotly_chart(fig2, use_container_width=True)

    elif choice == "Student Portal":
        st.title("Student Data")
        student_data = pd.DataFrame({
            "Student": ["Rahul", "Simran", "Aryan", "Neha", "Amit"],
            "Skill Match": [f"{x}%" for x in np.random.randint(60, 100, size=5)],
            "Assigned Mentor": ["James", "Dr. Neha", "James", "Dr. Neha", "James"]
        })
        st.table(student_data)

    elif choice == "Mentor Portal":
        st.title("Mentor Data")
        mentor_data = pd.DataFrame({
            "Mentor": ["Dr. Neha Verma", "James Carter", "Anil Kumar", "Priya Singh"],
            "Students Assigned": np.random.randint(2, 8, size=4),
            "Expertise": ["AI", "Product Mgmt", "Backend", "Finance"]
        })
        st.table(mentor_data)
