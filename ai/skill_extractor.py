import re

SKILLS = [
    "python",
    "java",
    "c++",
    "c#",
    "go",
    "rust",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",

    "flask",
    "fastapi",
    "django",
    "spring boot",
    "express",
    "node.js",

    "react",
    "angular",
    "vue",

    "docker",
    "kubernetes",

    "aws",
    "azure",
    "gcp",

    "git",
    "github",

    "tensorflow",
    "pytorch",
    "scikit-learn",

    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",

    "langchain",
    "llm",
    "rag",
    "openai",
    "genai",

    "linux",
    "rest api",
    "microservices"
]
def extract_skills(text):
    text = text.lower()

    found = []

    for skill in SKILLS:
        if skill.lower() in text:
            found.append(skill)

    return sorted(set(found))