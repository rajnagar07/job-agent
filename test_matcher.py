from ai.matcher import match_resume_with_ai

resume = """
Python Developer

Skills:
Python
Flask
FastAPI
SQL
Docker
Git
"""

job = """
Backend Engineer

Requirements:
Python
FastAPI
Docker
AWS
SQL
Git
Redis
"""

result = match_resume_with_ai(resume, job)

print(result)