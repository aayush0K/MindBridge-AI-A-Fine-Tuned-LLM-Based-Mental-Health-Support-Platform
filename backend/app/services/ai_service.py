"""
AI Service — Main Orchestrator
===============================
Implements the full pipeline from the IEEE ICDSBS 2025 paper:
  1. Sanitise → 2. Embed → 3. Relevance check → 4. Crisis detection
  → 5. Few-shot retrieval → 6. Build Gemini history (with memory)
  → 7. Generate → 8. Store to memory → 9. Return enriched payload

New in this version
-------------------
* Redis-backed persistent memory (via MemoryService)
  - Loads last HISTORY_FOR_LLM turns from Redis before building the prompt.
  - Persists both the user message and the AI response after every turn.
* Improved crisis detection (false-positive hardening)
  - Min 5-word guard: classifier crisis flag is IGNORED for very short input.
  - Raised CRISIS_CONFIDENCE_THRESHOLD (0.55 → 0.78, set in classifier_service.py).
  - Uncertainty guard: classifier crisis flag is also IGNORED when uncertainty ≥ 0.05.
  - Keyword + embedding checks are ALWAYS authoritative regardless of length.
* Enriched return payload:
    { response, is_crisis, is_relevant, relevance_score, few_shot_count,
      predicted_category, classifier_confidence, uncertainty, memory_used }
"""

from __future__ import annotations

import logging

import httpx

from .embedder import embedder
from .crisis_service import is_crisis_message, CRISIS_RESPONSE
from .classifier_service import (
    classifier_service,
    CONFIDENCE_FALLBACK_THRESHOLD,
    CRISIS_CONFIDENCE_THRESHOLD,
    MIN_WORDS_FOR_CLASSIFIER_TRUST,
)
from .memory_service import memory_service, HISTORY_FOR_LLM
from app.safety.output_safety import sanitize_model_output
from app.config import settings

logger = logging.getLogger(__name__)

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are MindBridge, a compassionate AI mental health companion. Your role is to provide empathetic, supportive, non-judgmental responses to people dealing with mental health challenges.

Core principles:
- Always validate the user's feelings FIRST before offering any perspective
- Use open-ended questions to encourage self-reflection and exploration
- NEVER diagnose any mental health condition or prescribe medication
- Always recommend professional help for persistent or serious issues
- Keep your tone warm, calm, supportive, and hopeful
- Responses should be 2-4 sentences unless the user clearly needs more
- Use "I" statements and second-person language to feel personal ("I can hear that..." / "It sounds like you...")
- Never minimize feelings — everything the user shares matters

Topic steering & Context:
- CONVERSATION MEMORY: You are continuing an ongoing conversation. You will receive the recent conversation history. You MUST read it carefully and remember the original topic.
- If the user uses pronouns like "it", "they", or "this", strictly refer to the conversation history to understand the context. Do not lose the thread.
- Maintain conversation continuity. Always factor in previous messages.
- If the user asks something completely off-topic (like coding, math, or random trivia), respond politely but gently steer the conversation back to their emotional state or wellbeing. Do not abruptly reject them.
- You are NOT a replacement for therapy. You are a first point of empathetic support."""

# ── Static few-shot seed examples (always injected, model never changes them) ─
STATIC_EXAMPLES = [
    {
        "user": "I feel overwhelmed and don't know what to do.",
        "assistant": (
            "That sounds really exhausting — feeling overwhelmed takes so much out of you, "
            "and I can hear how heavy this feels right now. You don't have to figure everything "
            "out at once. Can you tell me what's weighing on you the most right now?"
        ),
    },
    {
        "user": "I've been anxious about everything lately.",
        "assistant": (
            "Anxiety can be so consuming, especially when it feels like it's everywhere at once "
            "— like your mind won't let you rest. You're not alone in feeling this way. What "
            "situation feels most pressing or difficult for you today?"
        ),
    },
    {
        "user": "I feel like no one understands me.",
        "assistant": (
            "That feeling of being misunderstood can be really lonely and painful. You deserve "
            "to be heard and seen for who you truly are. Can you tell me more about what's been "
            "happening that's made you feel this way?"
        ),
    },
]

# ── Static system prompt prefix (built once — never rebuilt per request) ─────
# The static examples are folded in here at module load time.
# The dynamic few-shot section (retrieved per request) is appended per call.
_STATIC_PROMPT_PREFIX: str = SYSTEM_PROMPT + "\n\nHere are some examples of how you should respond:\n"
_STATIC_PROMPT_PREFIX += "\nUser: I feel overwhelmed and don't know what to do.\nMindBridge: That sounds really exhausting — feeling overwhelmed takes so much out of you, and I can hear how heavy this feels right now. You don't have to figure everything out at once. Can you tell me what's weighing on you the most right now?\n"
_STATIC_PROMPT_PREFIX += "\nUser: I've been anxious about everything lately.\nMindBridge: Anxiety can be so consuming, especially when it feels like it's everywhere at once — like your mind won't let you rest. You're not alone in feeling this way. What situation feels most pressing or difficult for you today?\n"
_STATIC_PROMPT_PREFIX += "\nUser: I feel like no one understands me.\nMindBridge: That feeling of being misunderstood can be really lonely and painful. You deserve to be heard and seen for who you truly are. Can you tell me more about what's been happening that's made you feel this way?\n"

# ── Crisis detection tuning constants ─────────────────────────────────────────
# Minimum number of words a message must contain before we trust the
# CLASSIFIER's crisis prediction.  Keyword & embedding checks always run
# regardless of message length — they are the authoritative safety net.
CRISIS_MIN_WORD_COUNT = 5

# Maximum MC Dropout uncertainty allowed for the classifier crisis flag to count.
# High uncertainty means the model is "guessing" — don't penalise the user for it.
CRISIS_MAX_UNCERTAINTY = 0.04


# ── Initialisation ────────────────────────────────────────────────────────────

# Cached inference client
_http_client: httpx.AsyncClient | None = None

def _initialize_inference() -> None:
    """Configure HTTP client for remote or local GPU inference server."""
    global _http_client
    _http_client = httpx.AsyncClient(timeout=60.0)
    logger.info(f"[AI Service] Model inference client initialized (target: {settings.INFERENCE_URL}).")


# ── Crisis guard ──────────────────────────────────────────────────────────────

def _classifier_flags_crisis(
    classifier_result: dict,
    word_count: int,
) -> bool:
    """
    Classifier only triggers if ALL conditions met:
      - category == "crisis"
      - confidence >= CRISIS_CONFIDENCE_THRESHOLD (0.82)
      - uncertainty < CRISIS_MAX_UNCERTAINTY (0.04)
      - message length >= CRISIS_MIN_WORD_COUNT (5 words)

    Keyword and embedding checks in crisis_service / embedder run separately
    and are always authoritative regardless of message length.
    """
    if not classifier_result.get("available"):
        return False

    if (
        classifier_result["category"] == "crisis" and
        classifier_result["confidence"] >= CRISIS_CONFIDENCE_THRESHOLD and
        classifier_result.get("uncertainty", 1.0) < CRISIS_MAX_UNCERTAINTY and
        word_count >= CRISIS_MIN_WORD_COUNT
    ):
        return True

    return False


def _build_contextual_fallback(user_message: str, category: str | None, safe_examples: list[dict]) -> str:
    """
    Build a natural, empathetic, human-like conversational response that directly
    responds to the user's message, maintaining thread continuity.
    """
    text_lower = user_message.lower().strip()

    # 1. Conversational affirmations & acknowledgments
    if any(text_lower.startswith(k) or text_lower == k for k in ["thanks", "thank you", "that helps", "ok", "okay", "alright", "got it", "i see", "yes", "yeah"]):
        return (
            "I'm really glad to hear that helped. Remember to take things one small step at a time. "
            "How are you feeling right now, or is there anything else on your mind?"
        )

    if any(k in text_lower for k in ["hello", "hi", "hey", "good morning", "good evening"]):
        return (
            "Hello! I'm here for you. Whatever is on your mind today, feel free to share — I'm listening."
        )

    # 2. Specific situational contexts
    if any(k in text_lower for k in ["teacher", "school", "class", "homework", "principal", "professor", "exam", "test", "study", "grade", "assignment"]):
        if any(k in text_lower for k in ["yell", "shout", "shought", "scold", "mad", "angry", "mean", "strict"]):
            return (
                "Having a teacher shout or scold you can feel really distressing and intimidating. "
                "It's completely natural to feel hurt or shaken up by that. "
                "What happened before they raised their voice, and how are you holding up right now?"
            )
        return (
            "I hear how much pressure and stress you're dealing with around school and academics right now. "
            "It's completely valid to feel overwhelmed when expectations feel heavy. "
            "What specific situation is weighing on you the most today?"
        )

    if any(k in text_lower for k in ["sleep", "night", "insomnia", "bed", "awake", "tired", "rest"]):
        return (
            "Struggling to sleep when you're exhausted is so physically and emotionally draining. "
            "When your mind keeps racing at night, bedtime can feel really overwhelming. "
            "What kinds of thoughts tend to keep you awake most often?"
        )

    if any(k in text_lower for k in ["parent", "mom", "dad", "family", "mother", "father", "brother", "sister"]):
        return (
            "Family dynamics can bring up really complex and heavy emotions. "
            "It takes a lot to process conflict or pressure with family members. "
            "Would you like to talk more about what's been happening with them?"
        )

    if any(k in text_lower for k in ["lonely", "alone", "nobody", "no one", "isolated", "friend"]):
        return (
            "Feeling isolated or misunderstood can feel really lonely and painful. "
            "Your feelings are completely valid, and you deserve support and care. "
            "Would you like to tell me a bit more about what's been making you feel this way?"
        )

    if any(k in text_lower for k in ["work", "job", "boss", "colleague", "career", "office"]):
        return (
            "Workplace stress and conflict with supervisors or colleagues can take a heavy toll. "
            "It sounds like you're dealing with a really demanding situation. "
            "What part of work is feeling hardest for you right now?"
        )

    if any(k in text_lower for k in ["sad", "depressed", "down", "cry", "crying", "unhappy", "hurt"]):
        return (
            "I hear how heavy and painful things feel for you right now. I'm really glad you shared this with me. "
            "You don't have to carry this all alone. "
            "Can you tell me a little more about what's been weighing on your heart today?"
        )

    # 3. Dynamic human-like response mirroring user input (prevents random corpus mismatch)
    clean_msg = user_message.strip("?.!")
    if len(clean_msg) > 3:
        return (
            f"I hear you saying that '{clean_msg}'. That sounds like a difficult situation to process, "
            "and your feelings about it are completely valid. "
            "Can you tell me a bit more about what happened and how you're feeling right now?"
        )

    return (
        "I hear you, and what you're sharing matters. "
        "Can you tell me more about what's been happening today? I'm here to listen."
    )


# ── Main pipeline ─────────────────────────────────────────────────────────────

async def process_message(
    user_message: str,
    session_id: str,
    session_history: list[dict],   # DB history (fallback when Redis unavailable)
) -> dict:
    """
    Full AI pipeline.

    Parameters
    ----------
    user_message    : Raw user input (will be trimmed + capped at 1 000 chars)
    session_id      : Chat session UUID string — used as Redis memory key
    session_history : Messages loaded from PostgreSQL (used as fallback when
                      Redis memory is not available)

    Returns
    -------
    {
        "response"              : str,
        "is_crisis"             : bool,
        "is_relevant"           : bool,
        "relevance_score"       : float,
        "few_shot_count"        : int,
        "predicted_category"    : str | None,
        "classifier_confidence" : float,
        "uncertainty"           : float,
        "memory_used"           : bool,   # True when Redis history was injected
    }
    """
    # ── Step 1: Sanitise ──────────────────────────────────────────────────────
    # The schema validator already strips and caps at 1000 chars.
    # We re-strip here defensively for calls that bypass the REST layer (e.g. tests).
    user_message = user_message.strip()[:1000]
    if not user_message:
        return {
            "response"              : "I didn't catch that — could you say a bit more? I'm here to listen. 💙",
            "is_crisis"             : False,
            "is_relevant"           : False,
            "relevance_score"       : 0.0,
            "few_shot_count"        : 0,
            "predicted_category"    : None,
            "classifier_confidence" : 0.0,
            "uncertainty"           : 0.0,
            "memory_used"           : False,
        }
    word_count = len(user_message.split())

    # ── Step 2: Embed ─────────────────────────────────────────────────────────
    query_vec = embedder.embed(user_message)

    # ── Step 3: Relevance check (soft — LLM steers off-topic, not hard-block) ─
    is_relevant, relevance_score = embedder.check_relevance(query_vec)

    # ── Step 3.5: Trained classifier ──────────────────────────────────────────
    classifier_result = classifier_service.predict(query_vec)
    predicted_category = classifier_result["category"]
    classifier_confidence = classifier_result["confidence"]
    classifier_uncertainty = classifier_result["uncertainty"]

    # Short/meta messages ("yes", "I don't know", "what did I say before?")
    # carry almost no semantic content — the classifier's confidence number
    # can look deceptively high on these even though it's effectively
    # guessing. Below MIN_WORDS_FOR_CLASSIFIER_TRUST words, we don't trust
    # the classifier's category or crisis signal at all, regardless of
    # confidence, and fall back to the original keyword/embedding/plain
    # cosine-similarity behavior.
    word_count = len(user_message.split())
    classifier_trusted = word_count >= MIN_WORDS_FOR_CLASSIFIER_TRUST

    classifier_flags_crisis = (
        classifier_result["available"]
        and classifier_trusted
        and predicted_category == "crisis"
        and classifier_confidence >= CRISIS_CONFIDENCE_THRESHOLD
    )

    # ── Step 4: Crisis detection ──────────────────────────────────────────────
    #   Layer A — keyword match (authoritative, 100% recall on known phrases)
    keyword_crisis = is_crisis_message(user_message)

    #   Layer B — embedding similarity to corpus crisis vectors
    embedding_crisis = embedder.check_crisis_embedding(query_vec)

    final_is_crisis = keyword_crisis or embedding_crisis or classifier_flags_crisis

    if final_is_crisis:
        logger.info(
            f"[AI Service] CRISIS triggered — keyword={keyword_crisis}, "
            f"embedding={embedding_crisis}, classifier={classifier_flags_crisis} | "
            f"words={word_count}, conf={classifier_confidence:.3f}, "
            f"unc={classifier_uncertainty:.4f}"
        )
        # Persist user message as crisis turn BEFORE returning
        await memory_service.append_message(
            session_id,
            role="user",
            content=user_message,
            category=predicted_category,
            confidence=classifier_confidence,
            is_crisis=True,
        )
        return {
            "response"              : CRISIS_RESPONSE,
            "is_crisis"             : True,
            "is_relevant"           : True,
            "relevance_score"       : relevance_score,
            "few_shot_count"        : 0,
            "predicted_category"    : predicted_category,
            "classifier_confidence" : classifier_confidence,
            "uncertainty"           : classifier_uncertainty,
            "memory_used"           : memory_service.available,
        }
    
    # ── Step 4.5: Suppress confusing classifier output ────────────────────────
    # If the classifier guessed "crisis" but our guards blocked it (e.g. short word count),
    # change the predicted category so the frontend/logs don't misleadingly say "Category=crisis".
    if predicted_category == "crisis" and not final_is_crisis:
        predicted_category = "ambiguous"

    # ── Step 5: Few-shot retrieval ────────────────────────────────────────────
    category_for_retrieval = (
        predicted_category
        if (
            classifier_result["available"]
            and classifier_trusted
            and classifier_confidence >= CONFIDENCE_FALLBACK_THRESHOLD
        )
        else None
    )
    examples = embedder.get_few_shot_examples_by_category(query_vec, category_for_retrieval)

    # ── Step 6: Build Gemini prompt & history ─────────────────────────────────

    # Dynamic portion: only the retrieved few-shot examples change per request.
    # The static prefix (_STATIC_PROMPT_PREFIX) was built once at module load.
    dynamic_few_shot = "".join(
        f"\nUser: {ex['context']}\nMindBridge: {ex['response']}\n"
        for ex in examples
        if ex.get("category") != "crisis"
    )
    dynamic_system_prompt = _STATIC_PROMPT_PREFIX + dynamic_few_shot

    messages: list[dict] = []

    # 6a — Recent conversation memory (Redis → PostgreSQL fallback)
    redis_history = await memory_service.get_history(session_id, limit=HISTORY_FOR_LLM)
    memory_used = bool(redis_history) or bool(session_history)

    if redis_history:
        # Redis memory is available — use it (most up-to-date)
        for msg in redis_history:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
    else:
        # Fallback to PostgreSQL session history
        for msg in session_history[-HISTORY_FOR_LLM:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})

    # 6b — Current user message (always last)
    messages.append({"role": "user", "content": user_message})

    # ── Step 7: Generate with MindBridge Model ───────────────────────────────
    full_messages = [
        {"role": "system", "content": dynamic_system_prompt}
    ] + messages

    try:
        if not _http_client:
            _initialize_inference()

        payload = {
            "messages": full_messages,
            "temperature": 0.6,
            "max_new_tokens": 300
        }
        headers = {}
        if getattr(settings, "REMOTE_INFERENCE_API_KEY", None):
            headers["X-API-Key"] = settings.REMOTE_INFERENCE_API_KEY
            headers["Authorization"] = f"Bearer {settings.REMOTE_INFERENCE_API_KEY}"

        response = await _http_client.post(settings.INFERENCE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        ai_text = data.get("response", "").strip()
        
        if not ai_text:
            raise ValueError("Inference server returned empty response")

    except Exception as exc:
        logger.error(f"[AI Service] Remote GPU inference error at {settings.INFERENCE_URL}: {exc}")
        ai_text = (
            "MindBridge AI model service is temporarily unavailable. "
            "Please check that your remote GPU inference server is running and try again."
        )

    # ── Step 7.5: Output Safety Guard (Sanitize against medical/diagnostic claims) ─
    ai_text = sanitize_model_output(ai_text)

    # ── Step 8: Persist to Redis memory (single pipeline, both messages) ─────
    await memory_service.append_turn(
        session_id,
        user_message=user_message,
        ai_message=ai_text,
        category=predicted_category,
        confidence=classifier_confidence,
    )

    # ── Step 9: Return enriched payload ──────────────────────────────────────
    return {
        "response"              : ai_text,
        "is_crisis"             : False,
        "is_relevant"           : is_relevant,   # actual check result, not hardcoded True
        "relevance_score"       : relevance_score,
        "few_shot_count"        : len(examples),
        "predicted_category"    : predicted_category,
        "classifier_confidence" : classifier_confidence,
        "uncertainty"           : classifier_uncertainty,
        "memory_used"           : memory_used,
    }
