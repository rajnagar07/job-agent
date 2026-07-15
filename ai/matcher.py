def calculate_match_score(resume_skills, job_skills):

    resume = set(skill.lower() for skill in resume_skills)
    job = set(skill.lower() for skill in job_skills)

    matched = resume.intersection(job)
    missing = job - resume

    if not job:
        score = 0
    else:
        score = int((len(matched) / len(job)) * 100)

    return {
        "score": score,
        "matched": sorted(matched),
        "missing": sorted(missing),
    }