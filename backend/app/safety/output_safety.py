"""
MindBridge AI — Output Safety Validator
=======================================
Inspects model-generated text to ensure it adheres to safety guidelines:
- No false claims of being a licensed doctor or psychologist
- No prescription or modification of psychiatric medications
- No definitive clinical diagnosis
- Appends medical disclaimer when necessary
"""

import re
from typing import Tuple

UNSAFE_OUTPUT_PATTERNS = [
    r"\b(i\s+diagnose\s+you\s+with|you\s+definitely\s+have\s+clinical\s+depression|you\s+have\s+bipolar\s+disorder)\b",
    r"\b(take\s+\d+\s*mg\s+of|stop\s+taking\s+your\s+medication|increase\s+your\s+dosage\s+to)\b",
    r"\b(as\s+your\s+doctor|i\s+am\s+a\s+licensed\s+psychiatrist|as\s+a\s+medical\s+professional)\b"
]

COMPILED_UNSAFE_OUTPUT = re.compile("|".join(UNSAFE_OUTPUT_PATTERNS), re.IGNORECASE)

DISCLAIMER_TEXT = "\n\n*(Note: MindBridge is an AI emotional-support assistant and does not provide medical diagnoses or prescriptions. Please consult a qualified mental health professional for clinical care.)*"

def sanitize_model_output(generated_text: str) -> str:
    """
    Validates and cleans model output.
    If unsafe claims or prescriptive statements are detected, replaces or modifies them.
    """
    cleaned = generated_text.strip()
    if not cleaned:
        return "I'm listening and here to support you. Could you tell me more about how you're feeling right now?"

    # Check for prohibited prescriptive or diagnostic output
    if COMPILED_UNSAFE_OUTPUT.search(cleaned):
        return (
            "I hear that you're going through a challenging situation. While I can offer empathetic support "
            "and coping strategies, I cannot provide a medical diagnosis or prescribe medication. "
            "I strongly encourage speaking with a licensed doctor or mental health professional who can provide "
            "personalized clinical guidance." + DISCLAIMER_TEXT
        )

    # Check if medical terminology was discussed and add gentle disclaimer if missing
    med_terms = ["antidepressant", "ssri", "medication", "psychiatrist", "dosage", "diagnosis", "disorder"]
    if any(term in cleaned.lower() for term in med_terms) and "professional" not in cleaned.lower():
        cleaned += DISCLAIMER_TEXT

    return cleaned
