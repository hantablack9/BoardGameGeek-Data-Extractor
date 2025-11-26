"""Pytest configuration and fixtures for BGG Extractor tests."""

import os

import pytest


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
        monkeypatch.setenv("BGG_API_TOKEN", "test-token-for-unit-tests")
