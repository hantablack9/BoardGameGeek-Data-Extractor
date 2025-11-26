"""Tests for synchronous client wrappers."""

import pytest

from bgg_extractor import (
    get_collection,
    get_family,
    get_plays,
    get_things,
    get_user,
    search,
)


def test_search_requires_token(monkeypatch):
    """Test that search raises ValueError when token is not set."""
    monkeypatch.delenv("BGG_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BGG_API_TOKEN is required"):
        search("query")


def test_get_things_requires_token(monkeypatch):
    """Test that get_things raises ValueError when token is not set."""
    monkeypatch.delenv("BGG_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BGG_API_TOKEN is required"):
        get_things([1, 2])


def test_get_collection_requires_token(monkeypatch):
    """Test that get_collection raises ValueError when token is not set."""
    monkeypatch.delenv("BGG_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BGG_API_TOKEN is required"):
        get_collection("user")


def test_get_plays_requires_token(monkeypatch):
    """Test that get_plays raises ValueError when token is not set."""
    monkeypatch.delenv("BGG_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BGG_API_TOKEN is required"):
        get_plays(username="user")


def test_get_family_requires_token(monkeypatch):
    """Test that get_family raises ValueError when token is not set."""
    monkeypatch.delenv("BGG_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BGG_API_TOKEN is required"):
        get_family([10])


def test_get_user_requires_token(monkeypatch):
    """Test that get_user raises ValueError when token is not set."""
    monkeypatch.delenv("BGG_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BGG_API_TOKEN is required"):
        get_user("user")
