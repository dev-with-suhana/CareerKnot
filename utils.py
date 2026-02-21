def career_roadmap(skills):
    roadmap = []

    if "python" in skills.lower():
        roadmap.append("Learn Data Structures")
        roadmap.append("Build Projects")
        roadmap.append("Practice System Design")
        roadmap.append("Apply for Backend Roles")

    if "machine learning" in skills.lower():
        roadmap.append("Master Statistics")
        roadmap.append("Build ML Projects")
        roadmap.append("Deploy Models")
        roadmap.append("Apply for ML Engineer Roles")

    return roadmap


def skill_gap(student_skills, mentor_skills):
    student_set = set(student_skills.lower().split(","))
    mentor_set = set(mentor_skills.lower().split(","))

    gap = mentor_set - student_set
    return list(gap)
