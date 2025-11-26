"""Pytest configuration and fixtures for BGG Extractor tests."""

import os

import pytest

# Dummy token used for unit tests with mocked HTTP responses
DUMMY_TOKEN = "test-token-for-unit-tests"  # noqa: S105


@pytest.fixture(autouse=True)
def set_bgg_api_token(monkeypatch):
    """Set a dummy BGG_API_TOKEN for all tests.

    This fixture automatically runs before each test and ensures that
    BGG_API_TOKEN is set in the environment. Unit tests use mocked HTTP
    responses (via respx), so they don't need a real token.

    If BGG_API_TOKEN is already set in the environment (e.g., for integration
    tests with real API calls), this fixture preserves that value.

    Args:
        monkeypatch: Pytest's monkeypatch fixture for modifying environment.
    """
    if not os.getenv("BGG_API_TOKEN"):
        monkeypatch.setenv("BGG_API_TOKEN", DUMMY_TOKEN)


def has_real_api_token():
    """Check if a real (non-dummy) BGG_API_TOKEN is available.

    Returns:
        bool: True if a real token is set, False otherwise.
    """
    token = os.getenv("BGG_API_TOKEN")
    return token is not None and token != DUMMY_TOKEN


# Skip integration tests if no real API token is available
skip_if_no_real_token = pytest.mark.skipif(
    not has_real_api_token(),
    reason="BGG_API_TOKEN not set or is dummy token; skipping integration tests that require real API access",
)
