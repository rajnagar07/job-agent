from ai.matcher import calculate_match_score

resume_skills = [
    "Python",
    "Flask",
    "Git",
    "SQL"
]

job_skills = [
    "Python",
    "FastAPI",
    "Docker",
    "Git",
    "SQL"
]

result = calculate_match_score(
    resume_skills,
    job_skills
)

print(result)