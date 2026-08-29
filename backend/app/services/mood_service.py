"""
Mood Detection Service
======================
Uses a pre-trained DistilBERT emotion classifier (GoEmotions, 28 labels) to
automatically detect the user's emotional state from their chat message.

The raw GoEmotions labels are grouped into 8 clinically-relevant mood
categories suitable for a mental-health dashboard and research paper:

    Happy, Sad, Anxious, Angry, Lonely, Stressed, Confused, Neutral

The service is loaded once at startup and reused across all requests.
"""

from __future__ import annotations

import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

# ── GoEmotions → MindBridge mood taxonomy mapping ─────────────────────────────
# GoEmotions has 28 fine-grained labels.  We collapse them into 8 categories
# that are meaningful for longitudinal mental-health tracking.
_EMOTION_MAP: dict[str, str] = {
    # Happy
    "joy": "Happy", "amusement": "Happy", "excitement": "Happy",
    "love": "Happy", "admiration": "Happy", "gratitude": "Happy",
    "pride": "Happy", "relief": "Happy", "optimism": "Happy",
    "caring": "Happy", "approval": "Happy", "desire": "Happy",
    # Sad
    "sadness": "Sad", "grief": "Sad", "remorse": "Sad",
    "disappointment": "Sad",
    # Anxious
    "nervousness": "Anxious", "fear": "Anxious",
    # Angry
    "anger": "Angry", "annoyance": "Angry", "disapproval": "Angry",
    "disgust": "Angry",
    # Lonely — no direct GoEmotions label, mapped from context
    "embarrassment": "Lonely",
    # Stressed
    "realization": "Stressed",
    # Confused
    "confusion": "Confused", "surprise": "Confused", "curiosity": "Confused",
    # Neutral
    "neutral": "Neutral",
}

# Mood score mapping (1-10 scale for the existing mood_logs table)
_MOOD_SCORES: dict[str, int] = {
    "Happy": 8,
    "Sad": 3,
    "Anxious": 3,
    "Angry": 2,
    "Lonely": 3,
    "Stressed": 4,
    "Confused": 5,
    "Neutral": 6,
}


class MoodDetector:
    """Singleton emotion classifier — loaded once, called per message."""

    def __init__(self):
        self._classifier = None

    def load(self):
        """Load the HuggingFace pipeline. Call once at app startup."""
        try:
            self._classifier = pipeline(
                "text-classification",
                model="bhadresh-savani/distilbert-base-uncased-emotion",
                top_k=1,
                truncation=True,
                max_length=512,
            )
            logger.info("[MoodService] Emotion classifier loaded successfully.")
        except Exception as e:
            logger.error(f"[MoodService] Failed to load emotion classifier: {e}")
            self._classifier = None

    def detect(self, text: str) -> dict:
        """
        Detect emotion from text.

        Returns
        -------
        {
            "mood_label": str,       # e.g. "Anxious"
            "mood_score": int,       # 1-10
            "confidence": float,     # 0.0 - 1.0
            "raw_label": str,        # Original model label
        }
        """
        if not self._classifier:
            return {
                "mood_label": "Neutral",
                "mood_score": 6,
                "confidence": 0.0,
                "raw_label": "unavailable",
            }

        try:
            result = self._classifier(text[:512])
            # pipeline with top_k=1 returns [[{label, score}]]
            top = result[0][0]
            raw_label = top["label"].lower()
            confidence = round(top["score"], 4)

            mood_label = _EMOTION_MAP.get(raw_label, "Neutral")
            mood_score = _MOOD_SCORES.get(mood_label, 6)

            return {
                "mood_label": mood_label,
                "mood_score": mood_score,
                "confidence": confidence,
                "raw_label": raw_label,
            }
        except Exception as e:
            logger.error(f"[MoodService] Detection error: {e}")
            return {
                "mood_label": "Neutral",
                "mood_score": 6,
                "confidence": 0.0,
                "raw_label": "error",
            }


# Module-level singleton
mood_detector = MoodDetector()
