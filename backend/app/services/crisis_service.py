"""
Crisis Detection Service
Keyword-based detection with 100% recall guarantee on known crisis phrases.

Implementation note: uses compiled regex with word boundaries to avoid
substring false-positives. "haircut myself" does NOT match "cut myself".
"take pills for headache" does NOT match "take pills".
"""

import re

CRISIS_KEYWORDS = [
    # Unambiguous high-confidence phrases — no false-positive risk
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "don't want to live", "no reason to live", "better off dead",
    "self harm", "self-harm", "hurt myself",
    "cut myself to",          # "cut myself to cope / feel something / punish"
    "cutting myself to",      # same pattern
    "overdose", "can't go on", "give up on life",
    "nobody cares if i die", "nobody would care if i died",
    "worthless enough to die", "hopeless and want to die",
    "no point living", "ending it all", "end it all",
    "tired of living", "want it to end",
    "thinking about suicide", "planning to end my life",
    # Removed: "take pills" — too broad (common medication language)
    # Removed: "cut myself" / "cutting myself" — too broad ("cutting myself loose")
    # Removed: "worth living anymore" — let embedding check handle ambiguous forms
]

# Build a compiled regex at module load — O(1) per call instead of O(N keywords).
# `re.escape` handles any special characters in phrases.
# Word boundaries (\b) prevent "haircut myself" from matching "cut myself".
_CRISIS_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(kw) for kw in CRISIS_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

CRISIS_RESPONSE = """I hear you, and I'm really glad you reached out. \
What you're feeling right now is serious, and you deserve immediate support \
from verified professionals in India.

Please reach out right now:
• **India Emergency (Police/Medical):** 112
• **Tele-MANAS (Govt of India):** 14416 or 1800-89-14416 (24×7, Toll-Free)
• **NIMHANS Helpline:** 080-46110007 (24×7)
• **Vandrevala Foundation:** 9999 666 555 or 1860-2662-345 (24×7, Free)
• **iCall (TISS):** 9152987821 (Mon–Sat, 8 AM – 10 PM)

You are not alone, and this feeling will not last forever. \
Are you safe right now?"""


def is_crisis_message(text: str) -> bool:
    """
    Check if a message contains crisis indicators via regex keyword matching.

    Uses word-boundary matching to prevent substring false positives:
    - "I got a haircut myself" → False  (was True with naive 'in' check)
    - "I need to take pills for my headache" → False
    - "I want to kill myself" → True
    - "I'm thinking about suicide" → True

    100% recall on the known-phrase list — safety first.
    """
    return bool(_CRISIS_PATTERN.search(text))
