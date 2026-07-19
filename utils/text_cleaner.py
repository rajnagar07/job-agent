import re


def clean_job_description(text):
    """
    Clean scraped job descriptions before displaying them.
    """

    if not text:
        return ""

    # -----------------------------
    # Convert HTML line breaks
    # -----------------------------
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # -----------------------------
    # Remove remaining HTML tags
    # -----------------------------
    text = re.sub(r"<[^>]+>", "", text)

    # -----------------------------
    # Remove hidden keyword instructions
    # -----------------------------
    spam_patterns = [
        r"Please mention.*?human\.",
        r"Please include.*?application\.",
        r"Companies can search these words.*",
        r"This is a beta feature.*",
    ]

    for pattern in spam_patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    # -----------------------------
    # Remove repeated spaces
    # -----------------------------
    text = re.sub(r"[ \t]+", " ", text)

    # -----------------------------
    # Remove repeated blank lines
    # -----------------------------
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()