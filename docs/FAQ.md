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
2. Provides verified Indian national helpline numbers (Tele-MANAS `14416` / `1800-89-14416` and Emergency `112`)
3. Persists the event in PostgreSQL (`crisis_flagged = true`) for audit purposes
4. Clears further AI generation — no GPU inference or cache lookup is executed for crisis messages

### What data is stored?

- **PostgreSQL**: User accounts, chat sessions, message history, mood logs, wellness reports, journal entries, and the reusable `semantic_cache`. Messages include `is_crisis` flag and `relevance_score`.
- **Redis**: Rolling conversation window (last 20 messages per session) — auto-deleted after 24 hours of inactivity.
- **Privacy Assurance**: Shared cache entries are filtered by a strict PII engine — names, phone numbers, emails, and personal disclosures are never stored.

---

## Architecture & Models

### What LLM does MindBridge AI use?

MindBridge AI runs a fine-tuned **Meta Llama-3-8B-Instruct** model adapted using **QLoRA** (`aayush0K/Llama-3-MindBridge`). It is hosted on a remote GPU server (such as Google Colab with a Tesla T4 GPU or local GPU node) and communicated with via an HTTP REST endpoint (`INFERENCE_URL`).

### How does Semantic Response Caching work?

Common or repetitive wellness inquiries are vectorized with `all-MiniLM-L6-v2` into 384-dimensional embeddings and matched against PostgreSQL using `pgvector` (`<=>` cosine distance with an HNSW index).
If the similarity is &ge; 0.90 and the emotional context is compatible, the cached guidance is returned in **~20 ms**, bypassing remote GPU execution and eliminating inference latency.

### What happens if the remote GPU is offline?

The backend handles this gracefully — if `INFERENCE_URL` cannot be reached, the server catches the timeout or connection failure and returns a non-fatal service notice without crashing. Crisis detection and semantic cache lookups still function normally.

### The server starts but corpus isn't loading — what's wrong?

Check that `CORPUS_PATH` in your `.env` points to the correct location. The default `./corpus/mental_health_corpus.json` is relative to the `backend/` directory. If you run `uvicorn` from a different directory, update the path accordingly.

### I'm getting `No trained weights found` on startup — is this a problem?

No. It means `backend/app/models/classifier_weights.pt` is absent. The system falls back to pure cosine-similarity retrieval — crisis keyword detection is unaffected. The weights file is committed to the repository and should be present after cloning.

### Redis won't connect on Windows

The `docker-compose.yml` maps Redis to **port 6380** (not the default 6379) to avoid conflicts with any existing local Redis instance. Make sure your `REDIS_URL` is `redis://localhost:6380`.

---

## AI Behavior

### Why doesn't the AI respond to off-topic questions?

The relevance gate uses cosine similarity to the mental health corpus. Off-topic queries (coding, recipes, geography, etc.) score below the 0.25 threshold. The LLM still responds, but the system prompt instructs it to gently steer back to wellbeing topics rather than engaging with unrelated content.

### Why do short messages like "yes" show `predicted_category: "ambiguous"`?

Messages shorter than 5 words are not trusted by the classifier — the confidence score is deceptively high on short inputs because the model has almost no semantic signal to go on. The category is overridden to `"ambiguous"` to prevent misleading frontend displays. This is intentional.

### Can the AI miss a crisis message?

The keyword layer uses compiled regex with word-boundary matching and covers all common known crisis phrases. It cannot miss a message that contains a listed phrase. The embedding and classifier layers add coverage for novel phrasings. However, oblique or highly ambiguous language may not be caught — crisis detection is probabilistic for non-keyword cases.

### The AI lost context from a previous message

Check `memory_used` in the response. If it is `false`, Redis was unavailable at the time. The PostgreSQL fallback is used, but it only covers messages persisted to the DB. Ensure Redis is running and reachable.

---

## Contributing

### Can I add more crisis keywords?

Yes. Edit `CRISIS_KEYWORDS` in `backend/app/services/crisis_service.py`. Add unambiguous phrases only — see the comments in that file for the removal rationale on phrases that generated false positives.

### How do I retrain the classifier?

The training script is in `backend/scripts/train_classifier.py`. Edit the corpus, run the script, and replace `backend/app/models/classifier_weights.pt` and `label_map.json` with the new outputs. Restart the server.
