# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x (latest) | ✅ Active |
| < 1.0 | ❌ No |

Only the latest release on the `main` branch receives security patches.

---

## Reporting a Vulnerability

**Please do NOT file a public GitHub issue for security vulnerabilities.**

Instead, send a detailed report to the maintainers via private channel (GitHub Security Advisory or email listed in the profile). We take all reports seriously.

### What to include

- A clear description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested mitigation (if you have one)

### Response timeline

| Stage | Target |
|---|---|
| Initial acknowledgement | 48 hours |
| Severity triage | 5 business days |
| Fix or mitigation published | 30 days for critical, 90 days for non-critical |

We practice coordinated disclosure: we will credit you in the changelog and release notes (unless you request anonymity).

---

## Security Design Decisions

### Authentication
- **JWT tokens** are stateless; access tokens expire in 30 minutes, refresh tokens in 30 days.
- **bcrypt** password hashing with rounds=12.
- `JWT_SECRET_KEY` has no default value — the server will refuse to start without one.
- The JWT `type` field (`access` / `refresh`) is validated on every request to prevent token-type confusion attacks.

### Secrets Management
- `JWT_SECRET_KEY` and optional `REMOTE_INFERENCE_API_KEY` are read from environment variables only.
- No secrets are committed to the repository (`.env` is in `.gitignore`).
- `.env.example` contains only placeholder values.

### Input Validation & Privacy
- All user messages are capped at 1000 characters before AI processing.
- Pydantic schemas validate and reject malformed request payloads at the HTTP boundary.
- CORS origins are strictly configured and configurable per environment.
- **Semantic Caching Privacy & PII Filter**: User messages are scanned for personal names, emails, phone numbers, and identifying disclosures before considering any response for the semantic cache. Responses containing personal disclosures are strictly excluded from shared caching.

### Crisis Safety
- The crisis detection pipeline uses 100%-recall keyword matching as its hard safety net.
- Crisis evaluation runs **prior to** any semantic cache lookup or model generation.
- The ML classifier is used as an **additional signal only** and never overrides the keyword check.
- Crisis responses always include verified helpline numbers (Tele-MANAS, 112); the system never diagnoses or dismisses.

### Data Retention
- Redis conversation memory auto-expires after 24 hours of inactivity (configurable via `MEMORY_TTL_SECONDS`).
- Deleting a chat session also clears its Redis memory.
- Semantic cache entries expire automatically based on `SEMANTIC_CACHE_TTL_DAYS` (default: 30 days).

---

## Out of Scope

The following are acknowledged and not treated as vulnerabilities for this project:
- Rate limiting (not yet implemented — see [ROADMAP.md](ROADMAP.md))
- Client-side token storage in browser localStorage (industry standard for single-page applications without custom cookie domains)
