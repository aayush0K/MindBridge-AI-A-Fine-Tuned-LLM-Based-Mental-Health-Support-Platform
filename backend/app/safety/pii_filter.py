"""
PII Filter & Reusability Guard
================================
Detects Personally Identifiable Information (PII), personal disclosures,
and verifies whether an AI-generated response is safe, generic, and
reusable for semantic caching. Also evaluates mood/context compatibility.
"""

from __future__ import annotations

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── PII Regex Patterns ────────────────────────────────────────────────────────
_EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

# Phone patterns: US/standard and Indian 10-digit formats
_PHONE_REGEX = re.compile(
    r"(?:\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b)|"
    r"(?:\b(?:\+91|91)?[-.\s]?[6-9]\d{9}\b)"
)

# Postal / Zip codes (US 5-digit and Indian 6-digit PIN codes)
_POSTAL_REGEX = re.compile(r"\b(?:\d{5}(?:-\d{4})?|\d{6})\b")

# Physical address indicators with numbers
_ADDRESS_REGEX = re.compile(
    r"\b\d+\s+[A-Za-z0-9\s,.-]{2,30}\s+(?:street|st\.|st|avenue|ave\.|ave|road|rd\.|rd|"
    r"lane|ln\.|ln|drive|dr\.|dr|boulevard|blvd\.|blvd|apartment|apt\.|apt|suite)\b",
    re.IGNORECASE,
)

# Explicit name disclosures
_NAME_DISCLOSURE_REGEX = re.compile(
    r"\b(?:my name is|i am|call me|i'm called|myself)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
    re.IGNORECASE,
)

# Relative / contact name disclosures ("my wife Sarah", "my friend Alex")
_NAMED_RELATION_REGEX = re.compile(
    r"\b(?:my\s+(?:husband|wife|daughter|son|mother|father|mom|dad|partner|friend|boss))\s+([A-Z][a-z]+)\b"
)

# Specific personal location disclosures
_LOCATION_DISCLOSURE_REGEX = re.compile(
    r"\b(?:i live in|i am living in|i stay in|my home is in|i moved to)\s+([A-Za-z\s]+)\b",
    re.IGNORECASE,
)

# Specific medication prescription disclosures
_PRESCRIPTION_REGEX = re.compile(
    r"\b(?:prescribed me|taking\s+\d+\s*(?:mg|ml)|dosage of\s+\d+)\b",
    re.IGNORECASE,
)

# Emergency hotline / crisis markers (must NOT be stored in generic semantic cache)
_CRISIS_MARKERS = [
    "tele-manas", "14416", "1800-89-14416", "112", "911", "suicide", "self-harm",
    "emergency services", "crisis lifeline", "helpline", "kill myself", "end my life"
]

# System error patterns
_ERROR_MARKERS = [
    "temporarily unavailable",
    "please check that your remote gpu",
    "inference error",
    "i didn't catch that",
    "an unexpected error occurred",
]


def contains_pii(text: str) -> bool:
    """
    Check whether a text string contains Personally Identifiable Information (PII)
    or sensitive personal disclosures.
    """
    if not text or not text.strip():
        return False

    clean_text = text.strip()

    if _EMAIL_REGEX.search(clean_text):
        return True

    if _PHONE_REGEX.search(clean_text):
        return True

    if _ADDRESS_REGEX.search(clean_text):
        return True

    if _NAME_DISCLOSURE_REGEX.search(clean_text):
        return True

    if _NAMED_RELATION_REGEX.search(clean_text):
        return True

    if _LOCATION_DISCLOSURE_REGEX.search(clean_text):
        return True

    if _PRESCRIPTION_REGEX.search(clean_text):
        return True

    return False


def is_reusable_guidance(query: str, response: str) -> bool:
    """
    Verify whether the question and AI response are suitable for caching.

    Criteria:
      1. Neither query nor response contains PII.
      2. Response is within valid length bounds (30 - 2000 chars).
      3. Response is NOT an error message or service downtime notice.
      4. Response does NOT contain crisis / emergency hotline text (crisis must
         always be detected live by the safety engine).
    """
    if not query or not response:
        return False

    q_clean = query.strip()
    r_clean = response.strip()

    # 1. PII Checks
    if contains_pii(q_clean) or contains_pii(r_clean):
        logger.info("[PIIFilter] Candidate rejected: contains PII.")
        return False

    # 2. Length Checks
    if len(r_clean) < 30 or len(r_clean) > 2000:
        logger.info(f"[PIIFilter] Candidate rejected: response length {len(r_clean)} out of bounds.")
        return False

    # 3. System Error Checks
    r_lower = r_clean.lower()
    if any(marker in r_lower for marker in _ERROR_MARKERS):
        logger.info("[PIIFilter] Candidate rejected: contains error notice.")
        return False

    # 4. Crisis Checks
    if any(marker in r_lower for marker in _CRISIS_MARKERS):
        logger.info("[PIIFilter] Candidate rejected: contains crisis/hotline content.")
        return False

    return True


# ── Mood Clusters & Compatibility ─────────────────────────────────────────────
_DISTRESS_MOODS = {"sadness", "fear", "anger", "disgust"}
_POSITIVE_MOODS = {"joy", "happiness", "gratitude"}


def is_mood_compatible(cached_mood: Optional[str], current_mood: Optional[str]) -> bool:
    """
    Evaluate whether a cached response generated under `cached_mood`
    is appropriate for a user whose current query reflects `current_mood`.

    Rules:
      - If either mood is missing or 'neutral', it is considered compatible.
      - If both moods are identical, compatible.
      - If one is severe distress (sadness/fear) and the other is positive (joy),
        they are INCOMPATIBLE (do not give a cheerful celebration to someone grieving,
        or a solemn grief response to someone expressing delight).
      - If one is 'anger' and the other is 'joy', they are INCOMPATIBLE.
    """
    if not cached_mood or not current_mood:
        return True

    c_mood = cached_mood.lower().strip()
    u_mood = current_mood.lower().strip()

    if c_mood in ("neutral", "unknown", "ambiguous") or u_mood in ("neutral", "unknown", "ambiguous"):
        return True

    if c_mood == u_mood:
        return True

    # Check cross-cluster conflict: Distress vs Positive
    if (c_mood in _DISTRESS_MOODS and u_mood in _POSITIVE_MOODS) or (
        c_mood in _POSITIVE_MOODS and u_mood in _DISTRESS_MOODS
    ):
        logger.info(
            f"[PIIFilter] Incompatible mood context: cached='{c_mood}' vs current='{u_mood}'."
        )
        return False

    # Conflicting negative emotion (e.g. explosive anger vs quiet despair)
    if (c_mood == "anger" and u_mood == "sadness") or (c_mood == "sadness" and u_mood == "anger"):
        return False

    return True
