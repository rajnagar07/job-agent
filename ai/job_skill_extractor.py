from ai.skill_extractor import extract_skills


def extract_job_skills(job):

    title = job.title if job.title else ""

    description = job.description if job.description else ""

    text = f"{title}\n{description}"

    return extract_skills(text)