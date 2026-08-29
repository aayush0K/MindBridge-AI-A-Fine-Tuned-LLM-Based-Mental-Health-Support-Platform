"""
MindBridge AI — Dedicated Model Service
=======================================
Phase 3: Dedicated Model Service that orchestrates model inference,
safety evaluation, and prompt templating.

The model is hosted on the inference microservice (:8001) or loaded once
at startup to avoid reloading 8B parameters per API call.
"""

import logging
import httpx
from typing import List, Dict, Any, Optional

from app.safety.input_safety import check_input_safety
from app.safety.output_safety import sanitize_model_output
from app.config import settings

logger = logging.getLogger(__name__)

# ── Official MindBridge System Prompt ──────────────────────────────────────────
MINDBRIDGE_SYSTEM_PROMPT = (
    "You are MindBridge, a compassionate, empathetic, and supportive AI mental wellness companion. "
    "Your role is to provide non-judgmental emotional support, attentive listening, stress-management suggestions, "
    "and healthy coping strategies, especially for students and individuals navigating challenging life situations.\n\n"
    "Core Principles:\n"
    "- Always validate the user's feelings with warmth, care, and kindness.\n"
    "- Maintain a supportive, understanding, and respectful tone at all times.\n"
    "- Suggest grounded, actionable coping exercises (such as deep breathing, journaling, or taking breaks).\n"
    "- Encourage speaking with a qualified healthcare or counseling professional for persistent struggles.\n"
    "- Never pretend to be human or a licensed medical professional.\n\n"
    "Strict Boundaries:\n"
    "- Under NO circumstances should you diagnose mental health conditions.\n"
    "- Do NOT claim to be a doctor, psychologist, or licensed therapist.\n"
    "- Do NOT prescribe, recommend, or modify medications or dosages.\n"
    "- Do NOT encourage or assist with self-harm or violence.\n"
    "- MindBridge is an AI wellness companion, not a replacement for qualified clinical care."
)

class ModelService:
    def __init__(self):
        self.inference_url = getattr(settings, "INFERENCE_URL", "http://localhost:8001/generate")
        self.http_client: Optional[httpx.AsyncClient] = None
        self.timeout = 30.0

    async def initialize(self):
        """Initializes the persistent HTTP client for local inference service."""
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=self.timeout)
            logger.info(f"[ModelService] Connected to inference microservice at {self.inference_url}")

    async def close(self):
        """Closes HTTP client session."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None

    async def generate_response(
        self,
        user_message: str,
        session_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 256,
        temperature: float = 0.6
    ) -> Dict[str, Any]:
        """
        Processes a user message through the input safety check, formats the prompt
        with conversation history and system guidelines, queries the fine-tuned model,
        and runs the output through the safety sanitizer.

        Returns:
            dict containing:
            - response: str
            - is_crisis: bool
            - safety_flag: Optional[str]
        """
        # ── 1. Input Safety Filter ───────────────────────────────────────────
        is_safe, safety_response, metadata = check_input_safety(user_message)
        if not is_safe:
            return {
                "response": safety_response,
                "is_crisis": metadata.get("is_crisis", False),
                "safety_flag": metadata.get("flag", "input_blocked")
            }

        # ── 2. Build Chat Messages ───────────────────────────────────────────
        messages = [{"role": "system", "content": MINDBRIDGE_SYSTEM_PROMPT}]

        # Inject recent conversation history if provided
        if session_history:
            for turn in session_history[-6:]:
                role = "user" if turn.get("role") == "user" else "assistant"
                messages.append({"role": role, "content": turn.get("content", "")})

        # Add current user message
        messages.append({"role": "user", "content": user_message.strip()})

        # ── 3. Query Inference Service ───────────────────────────────────────
        if not self.http_client:
            await self.initialize()

        raw_response_text = ""
        try:
            payload = {
                "messages": messages,
                "max_new_tokens": max_tokens,
                "temperature": temperature
            }
            response = await self.http_client.post(self.inference_url, json=payload)
            response.raise_for_status()
            data = response.json()
            raw_response_text = data.get("response", "").strip()

        except Exception as e:
            logger.warning(f"[ModelService] Inference service call failed ({e}). Using intelligent fallback.")
            raw_response_text = self._get_contextual_fallback(user_message)

        # ── 4. Output Safety Sanitization ────────────────────────────────────
        final_text = sanitize_model_output(raw_response_text)

        return {
            "response": final_text,
            "is_crisis": False,
            "safety_flag": None
        }

    def _get_contextual_fallback(self, text: str) -> str:
        """Graceful fallback if the GPU inference server is offline."""
        lower = text.lower()
        if any(w in lower for w in ["exam", "test", "study", "grade", "school", "college"]):
            return (
                "I hear how much academic pressure you're dealing with right now. "
                "Exams and coursework can feel overwhelming, but please remember to take short breaks and breathe. "
                "What specific topic or deadline is feeling heaviest today?"
            )
        elif any(w in lower for w in ["sleep", "night", "insomnia", "tired"]):
            return (
                "Having trouble sleeping when you're exhausted is physically and emotionally draining. "
                "Try writing down your thoughts before bed or practicing a simple 4-7-8 breathing exercise. "
                "I'm here to listen if you'd like to talk through what's on your mind."
            )
        elif any(w in lower for w in ["lonely", "alone", "isolated", "friend"]):
            return (
                "Feeling lonely is deeply painful, and it's completely valid to feel that way. "
                "Please know that you are not alone, and reaching out is a brave step. "
                "Would you like to share more about what's been happening recently?"
            )
        else:
            return (
                "Thank you for sharing that with me. I can hear that this situation is weighing on you. "
                "Take this one step at a time, and remember to treat yourself with kindness today. "
                "What do you think would bring you a small sense of relief right now?"
            )

# Global singleton instance
model_service = ModelService()
