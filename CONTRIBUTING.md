# Contributing to MindBridge AI

Thank you for your interest in contributing! This document explains how to get set up, the development workflow, and what we look for in contributions.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Testing](#testing)
- [Commit Style](#commit-style)
- [Pull Request Process](#pull-request-process)
- [Safety-Critical Code](#safety-critical-code)

---

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By contributing, you agree to abide by its terms.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/mindbridge-ai.git
   cd mindbridge-ai
   ```
3. **Add the upstream remote** so you can pull future changes:
   ```bash
   git remote add upstream https://github.com/your-org/mindbridge-ai.git
   ```

---

## Development Setup

### Infrastructure (required)
```bash
docker compose up -d
```
This starts PostgreSQL 16 (port 5435) and Redis 7 (port 6380).

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

pip install -r requirements.txt

cp .env.example .env
# Edit .env:
# - Set JWT_SECRET_KEY to any long random string for local dev
# - Set GEMINI_API_KEY if you have one (fallback works without it)

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000.

---

## Project Structure

```
mindbridge-ai/
├── backend/app/
│   ├── api/v1/       # FastAPI route handlers
│   ├── models/       # SQLAlchemy ORM models + trained classifier weights
│   ├── schemas/      # Pydantic schemas (request / response)
│   ├── services/     # Business logic (AI, auth, memory, embedder)
│   └── ws/           # WebSocket handler
├── backend/corpus/   # Mental health corpus JSON (training/retrieval data)
├── backend/tests/    # Unit and integration tests
├── frontend/         # Next.js 14 application
└── docs/             # Additional documentation
```

---

## How to Contribute

### Reporting Bugs

Please search existing issues before opening a new one. Include:
- Exact steps to reproduce
- Expected vs actual behavior
- Python/Node.js version, OS
- Relevant log output

### Suggesting Features

Open an issue with the `enhancement` label. Describe the problem you're solving, not just the solution.

### Submitting Code

1. Create a branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your changes.
3. Write or update tests.
4. Ensure the test suite passes.
5. Push and open a Pull Request against `main`.

---

## Testing

### Unit tests (no server required)
```bash
cd backend
python -m pytest tests/test_ai_pipeline.py -v
```

### Integration tests (server + Docker required)
```bash
# With the backend running:
python tests/e2e_test.py
```

All PRs must pass the unit test suite. If you change the AI pipeline, crisis detection thresholds, or memory service, please update the corresponding tests.

---

## Commit Style

We use conventional commits:

```
type(scope): short description

body (optional)
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`

Examples:
- `feat(crisis): add embedding-based crisis detection layer`
- `fix(memory): prevent race condition in Redis append_turn`
- `docs(readme): add architecture diagram`

---

## Pull Request Process

1. Reference any related issue in the PR description.
2. Describe **what** you changed and **why** (not just how).
3. Keep PRs focused — one concern per PR.
4. Respond to review feedback promptly.
5. A maintainer will squash-merge approved PRs.

---

## Safety-Critical Code

The crisis detection pipeline (`crisis_service.py`, `ai_service.py`) and any changes to crisis thresholds are treated as **safety-critical**. Changes here require:

- A clear written justification for the threshold change
- Evidence that genuine crisis messages are **not** missed (precision can go down; recall must not)
- Review from at least one maintainer before merge

When in doubt, keep existing crisis detection **more sensitive**, not less.

---

Thank you for making MindBridge AI better. 💙
