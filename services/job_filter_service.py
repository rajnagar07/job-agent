from __future__ import annotations

import json
import logging
import re
import ast
from functools import lru_cache
from typing import Any, Dict, Iterable, Mapping

from langchain_core.prompts import ChatPromptTemplate  # type: ignore

from ai.chatmodel import chat_model
import config

logger = logging.getLogger(__name__)


TITLE_PATTERNS = {
    r"\bsoftware engineer\b": 100,
    r"\bsoftware developer\b": 100,
    r"\bbackend engineer\b": 95,
    r"\bbackend developer\b": 95,
    r"\bfrontend engineer\b": 95,
    r"\bfrontend developer\b": 95,
    r"\bfull stack\b": 95,
    r"\bfull-stack\b": 95,
    r"\bfullstack\b": 95,
    r"\bpython developer\b": 95,
    r"\bpython engineer\b": 95,
    r"\bai engineer\b": 95,
    r"\bml engineer\b": 95,
    r"\bmachine learning engineer\b": 95,
    r"\bdata engineer\b": 95,
    r"\bdevops engineer\b": 95,
    r"\bplatform engineer\b": 90,
    r"\binfrastructure engineer\b": 90,
}

SKILL_KEYWORDS = {
    "python": 15,
    "flask": 15,
    "fastapi": 15,
    "django": 15,
    "java": 10,
    "spring": 10,
    "react": 10,
    "angular": 10,
    "vue": 10,
    "javascript": 10,
    "typescript": 10,
    "sql": 10,
    "postgresql": 10,
    "mysql": 10,
    "mongodb": 10,
    "docker": 10,
    "kubernetes": 10,
    "aws": 10,
    "azure": 10,
    "gcp": 10,
    "git": 5,
    "rest api": 5,
    "microservices": 10,
    "langchain": 20,
    "llm": 20,
    "rag": 20,
    "genai": 20,
    "nlp": 20,
    "system design": 10,
    "ci/cd": 10,
    "graphql": 10,
    "redis": 10,
}

EXCLUDE = [
    "ios",
    "android",
    "react native",
    "flutter",
    "sales",
    "marketing",
    "account executive",
    "customer success",
    "finance",
    "legal",
    "designer",
    "graphic designer",
    "ui designer",
    "ux designer",
    "hr",
    "human resources",
    "recruiter",
    "chef",
    "cook",
    "driver",
    "porter",
    "warehouse",
    "nurse",
    "doctor",
    "teacher",
    "civil engineer",
    "mechanical engineer",
    "electrical engineer",
    "support engineer",
    "technical support",
]

GEMINI_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_template(
    """
You are a strict job classification engine.

Classify whether the role is a software engineering job.

Rules:
- Return ONLY valid JSON.
- Do NOT include markdown, code fences, or explanations.
- Use ONLY the keys in the example.
- Set software_job to true only when the role is clearly software-related.
- Set software_job to false for recruiting, sales, marketing, HR, operations,
  support, finance, legal, design, and non-technical engineering roles.
- Confidence must be an integer from 0 to 100.
- Reason must be a short, specific sentence.

Return exactly:

{{
  "software_job": true,
  "confidence": 96,
  "reason": "Backend software engineering role."
}}

Job title: {title}
Company: {company}
Location: {location}
Description:
{description}
"""
)


def clean_text(text: Any) -> str:
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", str(text))
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def normalize_job(job: Mapping[str, Any]) -> Dict[str, Any]:
    title = job.get("title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    description = job.get("description", "")

    normalized_title = clean_text(title)
    normalized_company = clean_text(company)
    normalized_location = clean_text(location)
    normalized_description = clean_text(description)
    source = job.get("source") or ""
    url = job.get("url") or ""

    combined_text = " ".join(
        value
        for value in [
            normalized_title,
            normalized_company,
            normalized_location,
            normalized_description,
        ]
        if value
    )

    return {
        **dict(job),
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "source": source,
        "url": url,
        "normalized_title": normalized_title,
        "normalized_company": normalized_company,
        "normalized_location": normalized_location,
        "normalized_description": normalized_description,
        "normalized_text": combined_text,
    }


def _score_job_text(title: str, text: str) -> Dict[str, Any]:
    normalized_title = clean_text(title)
    normalized_text = clean_text(text)

    if any(word in normalized_text for word in EXCLUDE):
        return {
            "score": 0,
            "reason": "Role is clearly outside the software engineering pipeline.",
            "signals": ["exclude"],
        }

    score = 0
    signals: list[str] = []

    for pattern, points in TITLE_PATTERNS.items():
        if re.search(pattern, normalized_title):
            score += points
            signals.append(f"title:{pattern}")

    for skill, points in SKILL_KEYWORDS.items():
        if skill in normalized_text:
            score += points
            signals.append(f"skill:{skill}")

    if "engineer" in normalized_title or "developer" in normalized_title:
        score += 10
        signals.append("title:software-indicator")

    if any(term in normalized_text for term in ["api", "backend", "frontend", "full stack"]):
        score += 10
        signals.append("text:software-indicator")

    score = min(score, 100)

    if score >= config.JOB_FILTER_ACCEPT_THRESHOLD:
        reason = "Strong rule-based software engineering match."
    elif score <= config.JOB_FILTER_REJECT_THRESHOLD:
        reason = "Low software relevance from deterministic scoring."
    else:
        reason = "Borderline software relevance; needs Gemini verification."

    return {
        "score": score,
        "reason": reason,
        "signals": signals,
    }


def job_score(job: Mapping[str, Any]) -> int:
    normalized = normalize_job(job)
    return int(
        _score_job_text(
            normalized.get("normalized_title", ""),
            normalized.get("normalized_text", ""),
        )["score"]
    )


def score_job(job: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = normalize_job(job)
    return _score_job_text(
        normalized.get("normalized_title", ""),
        normalized.get("normalized_text", ""),
    )


def _extract_json(content: Any) -> Dict[str, Any]:
    if isinstance(content, list):
        content = "".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        )

    if not isinstance(content, str):
        raise ValueError("Gemini response was not a string.")

    content = content.strip()
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    candidates = [content]

    # If Gemini wraps the payload in prose, keep only the first JSON-like block.
    json_block = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if json_block:
        candidates.append(json_block.group(0).strip())

    last_error: Exception | None = None

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except Exception as exc:
            last_error = exc

        try:
            parsed = ast.literal_eval(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception as exc:
            last_error = exc

    raise ValueError(f"Unable to parse Gemini response: {content}") from last_error


@lru_cache(maxsize=2048)
def _classify_with_gemini_cached(
    title: str,
    company: str,
    location: str,
    description: str,
) -> str:
    chain = GEMINI_CLASSIFICATION_PROMPT | chat_model
    response = chain.invoke(
        {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
        }
    )
    return str(response.content)


def classify_job_with_gemini(job: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = normalize_job(job)
    raw_content = _classify_with_gemini_cached(
        normalized.get("normalized_title", ""),
        normalized.get("normalized_company", ""),
        normalized.get("normalized_location", ""),
        normalized.get("normalized_description", ""),
    )

    try:
        result = _extract_json(raw_content)
    except Exception as exc:
        logger.warning(
            "Gemini response could not be parsed; rejecting job. title=%s error=%s content=%r",
            normalized.get("title", ""),
            exc,
            raw_content,
        )
        return {
            "software_job": False,
            "confidence": 0,
            "reason": "Gemini returned an invalid response.",
        }

    required_keys = {"software_job", "confidence", "reason"}
    missing_keys = required_keys - set(result.keys())
    if missing_keys:
        logger.warning(
            "Gemini response missing keys; rejecting job. title=%s missing=%s content=%r",
            normalized.get("title", ""),
            sorted(missing_keys),
            result,
        )
        return {
            "software_job": False,
            "confidence": 0,
            "reason": "Gemini response missing required fields.",
        }

    software_job = result.get("software_job")
    confidence = result.get("confidence")
    reason = result.get("reason")

    if isinstance(software_job, str):
        software_job = software_job.strip().lower() in {"true", "1", "yes", "y"}

    if confidence is None:
        confidence = 0
    else:
        try:
            confidence = int(confidence)
        except Exception:
            confidence = 0

    if reason is None:
        reason = "Gemini response missing a reason."

    return {
        "software_job": bool(software_job),
        "confidence": confidence,
        "reason": str(reason).strip(),
    }


def evaluate_job(job: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = normalize_job(job)
    rule_result = score_job(normalized)
    score = int(rule_result["score"])

    if score >= config.JOB_FILTER_ACCEPT_THRESHOLD:
        return {
            **dict(job),
            "software_job": True,
            "decision": "accept",
            "filter_stage": "rule",
            "match_score": score,
            "confidence": 100,
            "reason": rule_result["reason"],
            "signals": rule_result["signals"],
        }

    if score <= config.JOB_FILTER_REJECT_THRESHOLD:
        return {
            **dict(job),
            "software_job": False,
            "decision": "reject",
            "filter_stage": "rule",
            "match_score": score,
            "confidence": 0,
            "reason": rule_result["reason"],
            "signals": rule_result["signals"],
        }

    gemini_result = classify_job_with_gemini(normalized)
    return {
        **dict(job),
        "software_job": bool(gemini_result["software_job"]),
        "decision": "accept" if gemini_result["software_job"] else "reject",
        "filter_stage": "gemini",
        "match_score": int(gemini_result["confidence"]),
        "confidence": int(gemini_result["confidence"]),
        "reason": gemini_result["reason"],
        "signals": rule_result["signals"],
    }


def filter_jobs(jobs: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    selected_jobs: list[Dict[str, Any]] = []
    total = 0
    rule_accepts = 0
    rule_rejects = 0
    gemini_reviews = 0
    gemini_accepts = 0
    gemini_rejects = 0

    for job in jobs:
        total += 1
        decision = evaluate_job(job)

        if decision["filter_stage"] == "rule" and decision["software_job"]:
            rule_accepts += 1
        elif decision["filter_stage"] == "rule":
            rule_rejects += 1
        else:
            gemini_reviews += 1
            if decision["software_job"]:
                gemini_accepts += 1
            else:
                gemini_rejects += 1

        logger.info(
            "Job filter decision | title=%s | score=%s | stage=%s | keep=%s | reason=%s",
            decision.get("title", ""),
            decision.get("match_score", 0),
            decision.get("filter_stage", ""),
            decision.get("software_job", False),
            decision.get("reason", ""),
        )

        if decision["software_job"]:
            selected_jobs.append(decision)

    logger.info(
        "Hybrid job filter summary | total=%s | selected=%s | rule_accepts=%s | rule_rejects=%s | gemini_reviews=%s | gemini_accepts=%s | gemini_rejects=%s",
        total,
        len(selected_jobs),
        rule_accepts,
        rule_rejects,
        gemini_reviews,
        gemini_accepts,
        gemini_rejects,
    )

    return selected_jobs


def classify_jobs(jobs: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    return filter_jobs(jobs)
