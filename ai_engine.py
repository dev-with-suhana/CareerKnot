from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match_mentors(student_profile, mentors):
    mentor_profiles = [m.get("skills","") + " " + m.get("industry","") for m in mentors]
    student_text = student_profile.get("skills","") + " " + student_profile.get("career_interest","")

    documents = mentor_profiles + [student_text]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    scores = similarity_scores.flatten()

    ranked = sorted(zip(mentors, scores), key=lambda x: x[1], reverse=True)

    return ranked[:5]
