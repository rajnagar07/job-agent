from services.resume_service import extract_resume_text
from ai.resume_analyzer import analyze_resume

text = extract_resume_text("uploads/a9076e5a-e4f7-400a-985c-a32e815a1ab4.pdf")

skills = analyze_resume(text)

print(skills)