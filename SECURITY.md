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
- `GEMINI_API_KEY` and `JWT_SECRET_KEY` are read from environment variables only.
- No secrets are committed to the repository (`.env` is in `.gitignore`).
- `.env.example` contains only placeholder values.

### Input Validation
- All user messages are capped at 1000 characters before AI processing.
- Pydantic schemas validate and reject malformed request payloads at the HTTP boundary.
- CORS origins are strictly configured and configurable per environment.

### Crisis Safety
- The crisis detection pipeline uses 100%-recall keyword matching as its hard safety net.
- The ML classifier is used as an **additional signal only** and never overrides the keyword check.
- Crisis responses always include verified helpline numbers; the system never diagnoses or dismisses.

### Data Retention
- Redis conversation memory auto-expires after 24 hours of inactivity (configurable via `MEMORY_TTL_SECONDS`).
- Deleting a chat session also clears its Redis memory.

---

## Out of Scope

The following are acknowledged and not treated as vulnerabilities for this project:
- Rate limiting (not yet implemented — see [ROADMAP.md](ROADMAP.md))
- Gemini API key theft via server-side SSRF (mitigated by the key being server-only)
