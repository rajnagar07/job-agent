# import json

# from ai.chatmodel import chat_model
# from ai.prompts import resume_skill_prompt


# def analyze_resume(resume_text):

#     chain = resume_skill_prompt | chat_model

#     response = chain.invoke({
#         "resume": resume_text
#     })

#     content = response.content.strip()

#     # Remove markdown if Gemini returns ```json ... ```
#     content = content.replace("```json", "").replace("```", "").strip()

#     data = json.loads(content)

#     return data["skills"]


from ai.chatmodel import chat_model
from ai.prompts import resume_skill_prompt


def analyze_resume(resume_text):

    chain = resume_skill_prompt | chat_model

    response = chain.invoke({
        "resume": resume_text
    })

    print(type(response))
    print(response)