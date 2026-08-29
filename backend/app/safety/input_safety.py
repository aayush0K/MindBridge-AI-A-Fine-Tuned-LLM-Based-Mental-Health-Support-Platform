"""
MindBridge AI — Input Safety Guard
==================================
Inspects incoming user queries before they reach the model pipeline.
Identifies high-risk crisis markers, self-harm intents, violence, or dangerous requests.
"""

import re
from typing import Tuple, Dict, Any
from .crisis_response import get_crisis_response

# High-risk crisis regex phrases
CRISIS_PATTERNS = [
    r"\b(kill\s+(my\s*self|me)|end\s+my\s+life|commit\s+suicide|suicidal)\b",
    r"\b(want\s+to\s+die|don['’]?t\s+want\s+to\s+live(\s+anymore)?|better\s+off\s+dead)\b",
    r"\b(self[- ]?harm|hurt\s+myself|cut\s+myself\s+to|cutting\s+myself\s+to)\b",
    r"\b(no\s+reason\s+to\s+live|no\s+point\s+in\s+living|ending\s+it\s+all|end\s+it\s+all)\b",
    r"\b(take\s+all\s+my\s+pills|overdose|tired\s+of\s+living|hopeless\s+and\s+want\s+to\s+die)\b",
    r"\b(planning\s+to\s+(die|end\s+my\s+life)|nobody\s+would\s+care\s+if\s+i\s+die[d]?)\b"
]

COMPILED_CRISIS_REGEX = re.compile("|".join(CRISIS_PATTERNS), re.IGNORECASE)

# Violence / Threat patterns
VIOLENCE_PATTERNS = [
    r"\b(how\s+to\s+make\s+a\s+bomb|how\s+to\s+kill\s+someone|shoot\s+up\s+a\s+school)\b",
    r"\b(commit\s+murder|how\s+to\s+poison\s+someone)\b"
]
COMPILED_VIOLENCE_REGEX = re.compile("|".join(VIOLENCE_PATTERNS), re.IGNORECASE)

# Prescription / Diagnosis seeking patterns
PRESCRIPTION_PATTERNS = [
    r"\b(prescribe\s+me|what\s+dose\s+of\s+xanax|what\s+antidepressant\s+should\s+i\s+take|increase\s+my\s+medication\s+dose)\b",
    r"\b(diagnose\s+me\s+with|do\s+i\s+have\s+schizophrenia|confirm\s+my\s+bipolar\s+diagnosis)\b"
]
COMPILED_MED_REGEX = re.compile("|".join(PRESCRIPTION_PATTERNS), re.IGNORECASE)

def check_input_safety(user_message: str) -> Tuple[bool, str | None, Dict[str, Any]]:
    """
    Evaluates the input query for safety constraints.

    Returns:
        is_safe (bool): True if input is safe to pass to LLM, False if an immediate safety response is triggered.
        safety_response (str | None): Overriding safe response if is_safe is False.
        metadata (dict): Safety diagnostic flags.
    """
    text = user_message.strip()
    if not text:
        return False, "I didn't catch that. Please feel free to share what is on your mind.", {"empty": True}

    # 1. Crisis / Self-Harm Check (Highest Priority)
    if COMPILED_CRISIS_REGEX.search(text):
        return False, get_crisis_response(), {"is_crisis": True, "flag": "self_harm"}

    # 2. Violence / Harm to Others Check
    if COMPILED_VIOLENCE_REGEX.search(text):
        return False, (
            "I cannot fulfill requests that involve violence or harm to others. "
            "If you are feeling overwhelmed with anger or distress, I am here to help you explore healthy, "
            "safe coping mechanisms."
        ), {"is_violence": True, "flag": "violence"}

    # 3. Medical Prescription / Diagnosis Request Guard
    if COMPILED_MED_REGEX.search(text):
        # We don't block the model, but we flag it so the system prompt / output guard enforces clinical disclaimers
        return True, None, {"is_medical_request": True, "flag": "medical_query"}

    return True, None, {"is_safe": True}
