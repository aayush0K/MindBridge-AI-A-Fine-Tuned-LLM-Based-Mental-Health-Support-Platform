# Roadmap

This document tracks planned features and improvements for MindBridge AI.

Completed items are tracked in [CHANGELOG.md](CHANGELOG.md).

---

## v1.1 — Reliability & Safety

**Target: Q3 2025**

- [ ] **Rate limiting** — per-user and per-IP request throttling (e.g. 60 req/min chat)
- [ ] **Crisis alert notification** — optional SMS/email to an emergency contact when crisis protocol activates
- [ ] **Classifier retraining** — larger, balanced dataset; multi-label support for comorbid presentations
- [ ] **Session search** — full-text search across past conversations
- [ ] **Webhook for crisis events** — allow operators to integrate with their own escalation systems
- [ ] **Pydantic v2 ConfigDict** — migrate `Settings` from deprecated `class Config` to `model_config = ConfigDict(...)`

---

## v1.2 — Insights & Admin

**Target: Q4 2025**

- [ ] **Conversation summarization** — automatic summary after 20+ messages in a session
- [ ] **Admin dashboard** — usage analytics, crisis event log, user management
- [ ] **Mood correlations** — link mood scores to conversation sentiment over time
- [ ] **Export** — let users export their conversation and mood history (GDPR compliance)
- [ ] **Session TTL configuration** — allow users to choose memory retention period

---

## v2.0 — Scale & Multimodal

**Target: 2026**

- [ ] **Horizontal scaling** — Redis Cluster support, stateless workers, read replicas
- [ ] **Multi-language** — Hindi, Spanish, French (via multilingual embeddings)
- [ ] **Voice input** — speech-to-text with Whisper or Google Speech API
- [ ] **Mobile app** — React Native (iOS + Android), sharing the existing REST/WebSocket API
- [ ] **RAG on personal history** — retrieve user-specific past turns as additional few-shot context
- [ ] **Audit logging** — immutable log of all crisis events for operator compliance

---

## Backlog (no milestone)

- Crisis chatbot warm-transfer integration (iCall API if available)
- A/B testing framework for prompt variants
- Explainability layer — show user why a response was generated
- Model quantization for lower-latency inference
- Custom corpus upload — allow organizations to supply domain-specific examples

---

## Not Planned

The following are explicitly out of scope for this project:

- **Diagnosis** — MindBridge will never diagnose any mental health condition
- **Medication advice** — any medication-related questions are referred to professionals
- **Replacing therapy** — the system is a first-line support companion, not a substitute for qualified care
