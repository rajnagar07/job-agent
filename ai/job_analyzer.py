from ai.chatmodel import chat_model
from ai.prompts import job_skill_prompt


def analyze_job(job_description):

    chain = job_skill_prompt | chat_model

    response = chain.invoke({
        "job": job_description
    })

    return response