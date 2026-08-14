from __future__ import annotations

import ast
import json
import logging
import re
from functools import lru_cache
from typing import Any, Dict, Iterable, Mapping

from langchain_core.prompts import ChatPromptTemplate

from ai.chatmodel import chat_model
import config


logger = logging.getLogger(__name__)

# ============================================================
# GEMINI SAFETY LIMIT
# ============================================================

MAX_GEMINI_REVIEWS = 5
_gemini_review_count = 0

# ============================================================
# TITLE SIGNALS
# ============================================================

TITLE_PATTERNS = {

    # -------------------------
    # Software Engineering
    # -------------------------

    r"\bsoftware engineer\b": 100,
    r"\bsoftware developer\b": 100,
    r"\bsoftware development engineer\b": 100,
    r"\bsde\b": 95,

    # Backend
    r"\bbackend engineer\b": 95,
    r"\bbackend developer\b": 95,
    r"\bbackend\b": 80,

    # Frontend
    r"\bfrontend engineer\b": 95,
    r"\bfrontend developer\b": 95,
    r"\bfrontend\b": 80,

    # Full Stack
    r"\bfull stack\b": 95,
    r"\bfull-stack\b": 95,
    r"\bfullstack\b": 95,

    # Python
    r"\bpython developer\b": 95,
    r"\bpython engineer\b": 95,

    # AI / ML
    r"\bai engineer\b": 95,
    r"\bartificial intelligence engineer\b": 95,
    r"\bml engineer\b": 95,
    r"\bmachine learning engineer\b": 95,
    r"\bmachine learning developer\b": 95,
    r"\bnlp engineer\b": 95,
    r"\bllm engineer\b": 95,
    r"\bgenai engineer\b": 95,

    # Data
    r"\bdata engineer\b": 95,
    r"\bdata engineering\b": 90,
    r"\banalytics engineer\b": 90,
    r"\bbig data engineer\b": 90,

    # Cloud / DevOps / Platform
    r"\bdevops engineer\b": 95,
    r"\bdevops developer\b": 90,
    r"\bsite reliability engineer\b": 95,
    r"\bsre\b": 90,
    r"\bplatform engineer\b": 90,
    r"\binfrastructure engineer\b": 90,
    r"\bcloud engineer\b": 90,
    r"\bsystems engineer\b": 85,
    r"\bsystem engineer\b": 85,

    # Application / Product Engineering
    r"\bapplication engineer\b": 90,
    r"\bapplication developer\b": 90,
    r"\bproduct engineer\b": 90,
    r"\bproduct software engineer\b": 95,

    # Security Engineering
    r"\bsecurity engineer\b": 90,
    r"\bcybersecurity engineer\b": 90,
    r"\bcloud security engineer\b": 90,

    # Web
    r"\bweb developer\b": 90,
    r"\bweb engineer\b": 90,
}


# ============================================================
# TECHNICAL SKILLS
# ============================================================

SKILL_KEYWORDS = {

    "python": 15,
    "java": 10,
    "c++": 10,
    "c#": 10,
    "go": 10,
    "rust": 10,

    "flask": 15,
    "fastapi": 15,
    "django": 15,
    "spring": 10,
    "spring boot": 10,

    "react": 10,
    "angular": 10,
    "vue": 10,
    "javascript": 10,
    "typescript": 10,
    "node.js": 10,
    "nodejs": 10,

    "sql": 10,
    "postgresql": 10,
    "mysql": 10,
    "mongodb": 10,
    "redis": 10,

    "docker": 10,
    "kubernetes": 10,

    "aws": 10,
    "azure": 10,
    "gcp": 10,

    "git": 5,
    "github": 5,

    "rest api": 5,
    "restful api": 5,
    "graphql": 10,
    "microservices": 10,

    "machine learning": 15,
    "deep learning": 15,
    "nlp": 15,
    "computer vision": 15,

    "llm": 20,
    "rag": 20,
    "genai": 20,
    "generative ai": 20,
    "langchain": 20,
    "openai": 15,
    "gemini": 15,

    "system design": 10,
    "ci/cd": 10,

    "linux": 5,
    "terraform": 10,
    "ansible": 10,
}


# ============================================================
# EXCLUSIONS
# IMPORTANT:
# These are mainly TITLE/ROLE exclusions.
# We do NOT reject a software job just because
# the description mentions "marketing", "sales", etc.
# ============================================================

EXCLUDE_TITLE_PATTERNS = [

    r"\bsales\b",
    r"\baccount executive\b",
    r"\bbusiness development\b",

    r"\bmarketing\b",
    r"\bmarketing manager\b",

    r"\bcustomer success\b",
    r"\bcustomer support\b",

    r"\brecruiter\b",
    r"\brecruiting\b",
    r"\bhuman resources\b",
    r"\bhr\b",

    r"\bfinance\b",
    r"\bfinancial analyst\b",
    r"\baccounting\b",

    r"\blegal\b",
    r"\blawyer\b",

    r"\bdesigner\b",
    r"\bgraphic designer\b",
    r"\bproduct designer\b",
    r"\bui designer\b",
    r"\bux designer\b",

    r"\bchef\b",
    r"\bcook\b",
    r"\bdriver\b",
    r"\bporter\b",
    r"\bwarehouse\b",

    r"\bnurse\b",
    r"\bdoctor\b",
    r"\bteacher\b",

    r"\bcivil engineer\b",
    r"\bmechanical engineer\b",
    r"\belectrical engineer\b",

    r"\bprogram manager\b",
    r"\btechnical program manager\b",
    r"\bproject manager\b",

    r"\boperations manager\b",
]


# ============================================================
# GEMINI PROMPT
# ============================================================

GEMINI_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_template(
    """
You are a strict job classification engine.

Determine whether the job is relevant to a software/technology
engineering candidate.

Return ONLY valid JSON.

Rules:

- software_job=true for software engineering, backend,
  frontend, full-stack, AI/ML, data engineering, DevOps,
  cloud, platform, infrastructure, application engineering,
  security engineering, SRE, or similar technical engineering roles.

- software_job=false for sales, marketing, HR, recruiting,
  finance, legal, design, customer success, non-technical
  operations, program management, and clearly non-technical roles.

- Do not reject a technical engineering job merely because
  the description mentions business, sales, marketing,
  customers, or other non-technical words.

- Confidence must be an integer from 0 to 100.

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


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def clean_text(text: Any) -> str:

    if not text:
        return ""

    text = re.sub(
        r"<[^>]+>",
        " ",
        str(text)
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.lower().strip()


# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(
    job: Mapping[str, Any]
) -> Dict[str, Any]:

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


# ============================================================
# TITLE EXCLUSION
# ============================================================

def is_excluded_title(title: str) -> bool:

    title = clean_text(title)

    for pattern in EXCLUDE_TITLE_PATTERNS:

        if re.search(
            pattern,
            title
        ):
            return True

    return False


# ============================================================
# RULE-BASED SCORING
# ============================================================

def _score_job_text(
    title: str,
    text: str
) -> Dict[str, Any]:

    normalized_title = clean_text(title)
    normalized_text = clean_text(text)

    # --------------------------------------------------------
    # Reject based primarily on TITLE
    # --------------------------------------------------------

    if is_excluded_title(
        normalized_title
    ):

        return {
            "score": 0,
            "reason": (
                "Role title is clearly outside "
                "the software engineering pipeline."
            ),
            "signals": ["exclude:title"],
        }

    score = 0
    signals = []

    # --------------------------------------------------------
    # Title patterns
    # --------------------------------------------------------

    for pattern, points in TITLE_PATTERNS.items():

        if re.search(
            pattern,
            normalized_title
        ):

            score += points

            signals.append(
                f"title:{pattern}"
            )

    # --------------------------------------------------------
    # Technical skills
    # --------------------------------------------------------

    for skill, points in SKILL_KEYWORDS.items():

        # Word-ish matching to reduce false positives
        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            normalized_text
        ):

            score += points

            signals.append(
                f"skill:{skill}"
            )

    # --------------------------------------------------------
    # General software indicators
    # --------------------------------------------------------

    if (
        "engineer" in normalized_title
        or "developer" in normalized_title
    ):

        score += 10

        signals.append(
            "title:technical-indicator"
        )

    if any(
        term in normalized_text
        for term in [
            "api",
            "backend",
            "frontend",
            "software development",
            "programming",
            "code",
            "coding",
            "microservices",
        ]
    ):

        score += 10

        signals.append(
            "text:software-indicator"
        )

    score = min(
        score,
        100
    )

    # --------------------------------------------------------
    # Decision reason
    # --------------------------------------------------------

    if score >= config.JOB_FILTER_ACCEPT_THRESHOLD:

        reason = (
            "Strong rule-based software "
            "engineering match."
        )

    elif score <= config.JOB_FILTER_REJECT_THRESHOLD:

        reason = (
            "Low software relevance from "
            "deterministic scoring."
        )

    else:

        reason = (
            "Borderline software relevance; "
            "needs Gemini verification."
        )

    return {
        "score": score,
        "reason": reason,
        "signals": signals,
    }


# ============================================================
# SCORE JOB
# ============================================================

def job_score(
    job: Mapping[str, Any]
) -> int:

    normalized = normalize_job(job)

    return int(
        _score_job_text(
            normalized.get(
                "normalized_title",
                ""
            ),
            normalized.get(
                "normalized_text",
                ""
            ),
        )["score"]
    )


def score_job(
    job: Mapping[str, Any]
) -> Dict[str, Any]:

    normalized = normalize_job(job)

    return _score_job_text(
        normalized.get(
            "normalized_title",
            ""
        ),
        normalized.get(
            "normalized_text",
            ""
        ),
    )


# ============================================================
# GEMINI JSON PARSER
# ============================================================

def _extract_json(
    content: Any
) -> Dict[str, Any]:

    if isinstance(
        content,
        Mapping
    ):

        if "text" in content:
            return _extract_json(
                content["text"]
            )

        if {
            "software_job",
            "confidence",
            "reason",
        }.issubset(content.keys()):

            return dict(content)

        for key in (
            "content",
            "output",
            "response"
        ):

            if key in content:

                try:
                    return _extract_json(
                        content[key]
                    )

                except Exception:
                    pass

    if isinstance(
        content,
        list
    ):

        text_parts = []

        for item in content:

            if isinstance(
                item,
                Mapping
            ):

                if "text" in item:
                    text_parts.append(
                        str(item["text"])
                    )

            elif isinstance(
                item,
                str
            ):

                text_parts.append(item)

        if text_parts:
            content = "".join(
                text_parts
            )

    if isinstance(
        content,
        dict
    ):
        return content

    if not isinstance(
        content,
        str
    ):

        raise ValueError(
            f"Gemini response has unsupported "
            f"type: {type(content)}"
        )

    content = content.strip()

    if not content:

        raise ValueError(
            "Gemini returned an empty response."
        )

    # Remove markdown fences

    if content.startswith("```"):

        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
        ).strip()

    # Direct JSON

    try:

        parsed = json.loads(
            content
        )

        if isinstance(
            parsed,
            dict
        ):

            return parsed

    except Exception:
        pass

    # Extract JSON object

    json_block = re.search(
        r"\{.*\}",
        content,
        flags=re.DOTALL,
    )

    if json_block:

        candidate = (
            json_block.group(0)
            .strip()
        )

        try:

            parsed = json.loads(
                candidate
            )

            if isinstance(
                parsed,
                dict
            ):

                return parsed

        except Exception:
            pass

        try:

            parsed = ast.literal_eval(
                candidate
            )

            if isinstance(
                parsed,
                dict
            ):

                return parsed

        except Exception:
            pass

    raise ValueError(
        f"Unable to parse Gemini response: "
        f"{content}"
    )


# ============================================================
# GEMINI CLASSIFICATION
# ============================================================

@lru_cache(
    maxsize=2048
)
def _classify_with_gemini_cached(
    title: str,
    company: str,
    location: str,
    description: str,
) -> Any:

    chain = (
        GEMINI_CLASSIFICATION_PROMPT
        | chat_model
    )

    response = chain.invoke(
        {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
        }
    )

    return response.content


def classify_job_with_gemini(
    job: Mapping[str, Any]
) -> Dict[str, Any]:

    normalized = normalize_job(
        job
    )

    raw_content = (
        _classify_with_gemini_cached(
            normalized.get(
                "normalized_title",
                ""
            ),
            normalized.get(
                "normalized_company",
                ""
            ),
            normalized.get(
                "normalized_location",
                ""
            ),
            normalized.get(
                "normalized_description",
                ""
            ),
        )
    )

    try:

        result = _extract_json(
            raw_content
        )

    except Exception as exc:

        logger.warning(
            "Gemini response could not be parsed; "
            "rejecting job. title=%s error=%s",
            normalized.get(
                "title",
                ""
            ),
            exc,
        )

        return {
            "software_job": False,
            "confidence": 0,
            "reason": (
                "Gemini returned an invalid response."
            ),
        }

    required_keys = {
        "software_job",
        "confidence",
        "reason",
    }

    missing_keys = (
        required_keys
        - set(result.keys())
    )

    if missing_keys:

        logger.warning(
            "Gemini response missing keys; "
            "rejecting job. title=%s missing=%s",
            normalized.get(
                "title",
                ""
            ),
            sorted(
                missing_keys
            ),
        )

        return {
            "software_job": False,
            "confidence": 0,
            "reason": (
                "Gemini response missing "
                "required fields."
            ),
        }

    software_job = (
        result.get(
            "software_job"
        )
    )

    confidence = (
        result.get(
            "confidence"
        )
    )

    reason = (
        result.get(
            "reason"
        )
    )

    if isinstance(
        software_job,
        str
    ):

        software_job = (
            software_job
            .strip()
            .lower()
            in {
                "true",
                "1",
                "yes",
                "y",
            }
        )

    try:

        confidence = int(
            confidence
        )

    except Exception:

        confidence = 0

    confidence = max(
        0,
        min(
            confidence,
            100
        )
    )

    if reason is None:

        reason = (
            "Gemini response missing "
            "a reason."
        )

    return {
        "software_job": bool(
            software_job
        ),
        "confidence": confidence,
        "reason": str(
            reason
        ).strip(),
    }

# ============================================================
# SAFE GEMINI CLASSIFICATION
# ============================================================

def safe_classify_job_with_gemini(
    job: Mapping[str, Any],
    score: int,
    rule_result: Mapping[str, Any],
) -> Dict[str, Any] | None:

    global _gemini_review_count

    # --------------------------------------------------------
    # Prevent excessive Gemini API calls
    # --------------------------------------------------------

    # ========================================================
# BORDERLINE → GEMINI
# ========================================================

    if _gemini_review_count >= MAX_GEMINI_REVIEWS:

        # Gemini budget exhausted.
        # Use rule-based fallback directly.
        fallback_keep = score >= 50

        return {
            **dict(job),

            "software_job": fallback_keep,

            "decision": (
                "accept"
                if fallback_keep
                else "reject"
            ),

            "filter_stage": "rule_fallback",

            "filter_score": score,

            "confidence": score,

            "reason": (
                "Gemini review limit reached; "
                "decision made using rule-based fallback."
            ),

            "signals": rule_result["signals"],
        }

    # Count this actual Gemini attempt
    _gemini_review_count += 1

    logger.debug(
        "Gemini API review %s/%s | title=%s",
        _gemini_review_count,
        MAX_GEMINI_REVIEWS,
        job.get("title", "")
    )

    try:

        return classify_job_with_gemini(
            job
        )

    except Exception as exc:

        logger.warning(
            "Gemini classification failed. "
            "Using rule-based fallback. "
            "title=%s | error=%s",

            job.get(
                "title",
                ""
            ),

            exc
        )

        return None

# ============================================================
# FINAL JOB EVALUATION
# ============================================================

def evaluate_job(
    job: Mapping[str, Any]
) -> Dict[str, Any]:

    normalized = normalize_job(
        job
    )

    rule_result = score_job(
        normalized
    )

    score = int(
        rule_result["score"]
    )

    # ========================================================
    # STRONG RULE-BASED ACCEPT
    # ========================================================

    if (
        score
        >= config.JOB_FILTER_ACCEPT_THRESHOLD
    ):

        return {
            **dict(job),

            "software_job": True,
            "decision": "accept",

            "filter_stage": "rule",

            "filter_score": score,

            "confidence": 100,

            "reason": rule_result[
                "reason"
            ],

            "signals": rule_result[
                "signals"
            ],
        }

    # ========================================================
    # CLEAR RULE-BASED REJECT
    # ========================================================

    if (
        score
        <= config.JOB_FILTER_REJECT_THRESHOLD
    ):

        return {
            **dict(job),

            "software_job": False,
            "decision": "reject",

            "filter_stage": "rule",

            "filter_score": score,

            "confidence": 0,

            "reason": rule_result[
                "reason"
            ],

            "signals": rule_result[
                "signals"
            ],
        }

    # ========================================================
    # BORDERLINE → GEMINI
    # ========================================================

    gemini_result = (
        safe_classify_job_with_gemini(
            normalized,
            score,
            rule_result,
        )
    )

    # ========================================================
    # GEMINI UNAVAILABLE → RULE FALLBACK
    # ========================================================

    if gemini_result is None:

        # Conservative fallback:
        # borderline jobs are accepted only when
        # rule score is reasonably strong.

        fallback_keep = (
            score >= 50
        )

        return {
            **dict(job),

            "software_job": fallback_keep,

            "decision": (
                "accept"
                if fallback_keep
                else "reject"
            ),

            "filter_stage": "rule_fallback",

            "filter_score": score,

            "confidence": score,

            "reason": (
                "Gemini unavailable; "
                "decision made using "
                "rule-based fallback."
            ),

            "signals": rule_result[
                "signals"
            ],
        }

    # ========================================================
    # GEMINI RESULT
    # ========================================================

    software_job = bool(
        gemini_result[
            "software_job"
        ]
    )

    confidence = int(
        gemini_result[
            "confidence"
        ]
    )

    return {
        **dict(job),

        "software_job": software_job,

        "decision": (
            "accept"
            if software_job
            else "reject"
        ),

        "filter_stage": "gemini",

        "filter_score": confidence,

        "confidence": confidence,

        "reason": gemini_result[
            "reason"
        ],

        "signals": rule_result[
            "signals"
        ],
    }

# ============================================================
# FILTER JOBS
# ============================================================

def filter_jobs(
    jobs: Iterable[
        Mapping[str, Any]
    ]
) -> list[Dict[str, Any]]:

    global _gemini_review_count

    _gemini_review_count = 0
    selected_jobs = []

    total = 0
    rule_accepts = 0
    rule_rejects = 0

    gemini_reviews = 0
    gemini_accepts = 0
    gemini_rejects = 0

    for job in jobs:

        total += 1

        decision = evaluate_job(
            job
        )

        if (
            decision["filter_stage"]
            == "rule"
            and decision[
                "software_job"
            ]
        ):

            rule_accepts += 1

        elif (
            decision["filter_stage"]
            == "rule"
        ):

            rule_rejects += 1

        else:

            gemini_reviews += 1

            if decision[
                "software_job"
            ]:

                gemini_accepts += 1

            else:

                gemini_rejects += 1

        logger.debug(
            "Job filter decision | "
            "title=%s | score=%s | "
            "stage=%s | keep=%s | "
            "reason=%s",

            decision.get(
                "title",
                ""
            ),

            decision.get(
                "filter_score",
                0
            ),

            decision.get(
                "filter_stage",
                ""
            ),

            decision.get(
                "software_job",
                False
            ),

            decision.get(
                "reason",
                ""
            ),
        )

        if decision[
            "software_job"
        ]:

            selected_jobs.append(
                decision
            )

    logger.debug(
        "Hybrid job filter summary | "
        "total=%s | selected=%s | "
        "rule_accepts=%s | "
        "rule_rejects=%s | "
        "gemini_reviews=%s | "
        "gemini_accepts=%s | "
        "gemini_rejects=%s",

        total,
        len(selected_jobs),
        rule_accepts,
        rule_rejects,
        gemini_reviews,
        gemini_accepts,
        gemini_rejects,
    )

    return selected_jobs


# ============================================================
# Compatibility
# ============================================================

def classify_jobs(
    jobs: Iterable[
        Mapping[str, Any]
    ]
) -> list[Dict[str, Any]]:

    return filter_jobs(
        jobs
    )