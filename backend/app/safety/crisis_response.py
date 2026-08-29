"""
MindBridge AI — India Crisis Response Module
============================================
Provides structured, safe, empathetic crisis escalation messages with
verified Government of India emergency lines and national mental health helplines.
"""

CRISIS_RESPONSE_TEXT = """I hear how much pain you are in right now, and I want you to know that you do not have to carry this alone. What you are going through is serious, and your life has immense value.

Please connect with verified emergency or mental-health support in India right this moment:

🚨 **Emergency (India):**
• **National Unified Emergency:** Call **112** (For immediate danger or emergency)

🧠 **National Mental Health Helplines (India):**
• **Tele-MANAS (Govt of India):** Call **14416** or **1800-89-14416** (24×7, Toll-free across India)
• **NIMHANS Helpline:** Call **080-46110007** (24×7, Apex Mental Health Institute)
• **Vandrevala Foundation:** Call **9999 666 555** or **1860-2662-345** (24×7, Free counseling)
• **iCall (TISS):** Call **9152987821** (Mon–Sat, 8 AM – 10 PM)

💙 **Right now:**
Please stay in a safe space, take slow breaths, and reach out immediately to one of the helplines above, to a doctor, or to a trusted loved one.

Are you in a safe place right now?"""


def get_crisis_response(user_name: str | None = None) -> str:
    """Returns the standardized India crisis intervention message."""
    return CRISIS_RESPONSE_TEXT
