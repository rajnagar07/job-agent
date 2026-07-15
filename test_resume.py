from services.resume_service import extract_resume_text
from ai.skill_extractor import extract_skills

text = extract_resume_text("uploads/a9076e5a-e4f7-400a-985c-a32e815a1ab4.pdf")

skills = extract_skills(text)

print("\nExtracted Skills:\n")

for skill in skills:
    print("✔", skill)