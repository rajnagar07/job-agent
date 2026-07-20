# import json

# from ai.chatmodel import chat_model
# from ai.prompts import resume_analysis_prompt


# def analyze_resume_with_ai(resume_text):

#     try:

#         chain = resume_analysis_prompt | chat_model

#         response = chain.invoke({
#             "resume": resume_text
#         })

#         if isinstance(response.content, list):
#             content = response.content[0]["text"]
#         else:
#             content = response.content

#         content = content.strip()
#         # Remove ```json ... ```
#         content = (
#             content.replace("```json", "")
#                    .replace("```", "")
#                    .strip()
#         )

#         return json.loads(content)

#     except Exception as e:
#         print(type(response))
#         print(type(response.content))
#         print(response.content)

#         return {
#             "ats_score": 0,
#             "resume_score": 0,
#             "verdict": "Analysis Failed",
#             "summary": "Unable to analyze resume.",
#             "skills": [],
#             "strengths": [],
#             "weaknesses": [str(e)],
#             "recommendations": [],
#             "recommended_roles": []
#         }

import json

from ai.chatmodel import chat_model
from ai.prompts import resume_analysis_prompt


def analyze_resume_with_ai(resume_text):

    try:

        chain = resume_analysis_prompt | chat_model

        response = chain.invoke({
            "resume": resume_text
        })

        if isinstance(response.content, list):

            content = ""

            for block in response.content:
                if isinstance(block, dict) and block.get("type") == "text":
                    content += block["text"]

        else:

            content = response.content

        content = (
            content.replace("```json", "")
                   .replace("```", "")
                   .strip()
        )

        return json.loads(content)

    except Exception as e:

        # print("=" * 60)
        # print("RESUME ANALYZER ERROR")
        # print(e)
        # print("=" * 60)

        return {
            "ats_score": 0,
            "resume_score": 0,
            "verdict": "Analysis Failed",
            "summary": "Unable to analyze resume.",
            "skills": [],
            "strengths": [],
            "weaknesses": [str(e)],
            "recommendations": [],
            "recommended_roles": []
        }