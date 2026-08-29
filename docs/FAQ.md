# Frequently Asked Questions

---

## General

### What is MindBridge AI?

MindBridge AI is an open-source AI companion that provides empathetic first-line mental health support through conversation. It is not a replacement for licensed therapy or clinical care — it is a first point of empathetic contact.

### Is this a medical device?

No. MindBridge AI is a software application, not a medical device. It does not diagnose, treat, or prescribe for any mental health condition.

### What happens when someone sends a crisis message?

The system activates a crisis protocol that:
1. Immediately returns a compassionate response acknowledging the user's distress
2. Provides verified helpline numbers (India-specific + international via findahelpline.com)
3. Persists the event in PostgreSQL (`crisis_flagged = true`) for audit purposes
4. Clears further AI generation — no Gemini call is made for crisis messages

### What data is stored?

- **PostgreSQL**: User accounts, chat sessions, message history, mood logs. Messages include `is_crisis` flag and `relevance_score`.
- **Redis**: Rolling conversation window (last 20 messages per session) — auto-deleted after 24 hours of inactivity.
- No analytics, no third-party tracking, no cross-user data sharing.

---

## Setup

### Do I need a Gemini API key to run locally?

No. The system has a graceful fallback: if `GEMINI_API_KEY` is not set or if the Gemini API is unavailable, it returns the best-matching corpus example response instead. Crisis detection and relevance filtering still work fully without the key.

### The server starts but corpus isn't loading — what's wrong?

Check that `CORPUS_PATH` in your `.env` points to the correct location. The default `./corpus/mental_health_corpus.json` is relative to the `backend/` directory. If you run `uvicorn` from a different directory, update the path accordingly.

### I'm getting `No trained weights found` on startup — is this a problem?

No. It means `backend/app/models/classifier_weights.pt` is absent. The system falls back to pure cosine-similarity retrieval — crisis keyword detection is unaffected. The weights file is committed to the repository and should be present after cloning.

### Redis won't connect on Windows

The `docker-compose.yml` maps Redis to **port 6380** (not the default 6379) to avoid conflicts with any existing local Redis instance. Make sure your `REDIS_URL` is `redis://localhost:6380`.

### Gemini returns 429 Too Many Requests

You've hit the free tier rate limit. The backend handles this gracefully — it logs the error and returns a corpus fallback response. For production workloads, use a paid Gemini tier.

---

## AI Behavior

### Why doesn't the AI respond to off-topic questions?

The relevance gate uses cosine similarity to the mental health corpus. Off-topic queries (coding, recipes, geography, etc.) score below the 0.25 threshold. The LLM still responds, but the system prompt instructs it to gently steer back to wellbeing topics rather than engaging with unrelated content.

### Why do short messages like "yes" show `predicted_category: "ambiguous"`?

Messages shorter than 4 words are not trusted by the classifier — the confidence score is deceptively high on short inputs because the model has almost no semantic signal to go on. The category is overridden to `"ambiguous"` to prevent misleading frontend displays. This is intentional.

### Can the AI miss a crisis message?

The keyword layer uses compiled regex with word-boundary matching and covers all common known crisis phrases. It cannot miss a message that contains a listed phrase. The embedding and classifier layers add coverage for novel phrasings. However, oblique or highly ambiguous language may not be caught — crisis detection is probabilistic for non-keyword cases.

### The AI lost context from a previous message

Check `memory_used` in the response. If it is `false`, Redis was unavailable at the time. The PostgreSQL fallback is used, but it only covers messages persisted to the DB — very recent messages in the same request may not appear in the fallback history. Ensure Redis is running and reachable.

---

## Contributing

### Can I add more crisis keywords?

Yes. Edit `CRISIS_KEYWORDS` in `backend/app/services/crisis_service.py`. Add unambiguous phrases only — see the comments in that file for the removal rationale on phrases that generated false positives.

### How do I retrain the classifier?

The training script is in `backend/scripts/train_classifier.py`. Edit the corpus, run the script, and replace `backend/app/models/classifier_weights.pt` and `label_map.json` with the new outputs. Restart the server.

### Can I use a different LLM instead of Gemini?

The Gemini integration is encapsulated in `_initialize_gemini()` and the `generate_content` call in `ai_service.py`. Replacing it with another provider requires modifying `Step 7` of the pipeline and adjusting the message format (OpenAI uses a different dict structure than Gemini's `{role, parts}` format).
