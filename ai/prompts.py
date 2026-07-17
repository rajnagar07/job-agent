from langchain_core.prompts import ChatPromptTemplate # type: ignore

resume_skill_prompt = ChatPromptTemplate.from_template("""
You are an expert technical recruiter.

Extract ONLY the technical skills from the following resume.

Rules:
- Return ONLY valid JSON.
- Do not include any explanation.
- Normalize skill names (e.g., "JS" -> "JavaScript").

Format:

{{
    "skills": []
}}

Resume:

{resume}
""")


job_skill_prompt = ChatPromptTemplate.from_template("""
You are an expert technical recruiter.

Analyze the following job description.

Extract ONLY the technical skills.

Return ONLY valid JSON.

Format:

{
    "skills":[]
}

Job Description:

{job}
""")

match_prompt = ChatPromptTemplate.from_template("""
You are an expert technical recruiter.

Compare the following resume and job description.

Evaluate:
- Technical skill match
- Relevant experience
- Missing skills
- Overall suitability

Return ONLY valid JSON.

Format:

{{
  "match_score": 0,
  "matched_skills": [],
  "missing_skills": [],
  "strengths": [],
  "recommendation": ""
}}

Resume:
{resume}

Job Description:
{job}
""")