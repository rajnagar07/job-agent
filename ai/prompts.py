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