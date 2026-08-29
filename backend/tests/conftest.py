"""
conftest.py — pytest shared fixtures for the MindBridge test suite.

Provides:
  - `client`: an httpx.Client connected to the running backend
  - `token`: a valid JWT access token from a registered test user

Prerequisites (for integration tests only):
  - Docker services running: `docker compose up -d`
  - Backend running: `uvicorn app.main:app --reload` (from backend/)
  - The TEST_EMAIL / TEST_PASS user must exist in the database.
    Register them first if needed, or let `get_or_create_token` auto-register.
"""

from __future__ import annotations

import pytest
import httpx

BASE_URL   = "http://localhost:8000"
TEST_EMAIL = "test@mindbridge.ai"
TEST_PASS  = "TestPass123!"


def _get_or_create_token(client: httpx.Client) -> str:
    """
    Try to login; if that fails (user not yet registered), register first.
    This makes the test suite self-bootstrapping.
    """
    # Try login
    r = client.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASS},
    )
    if r.status_code == 200:
        return r.json()["access_token"]

    # Auto-register if login failed
    r = client.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASS, "full_name": "Test User"},
    )
    assert r.status_code == 201, f"Auto-register failed: {r.status_code} — {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def client() -> httpx.Client:
    """A synchronous HTTP client for the running backend, shared across all tests."""
    with httpx.Client(base_url=BASE_URL, timeout=90) as c:
        yield c


@pytest.fixture(scope="session")
def token(client: httpx.Client) -> str:
    """A valid JWT access token for the test user."""
    return _get_or_create_token(client)
