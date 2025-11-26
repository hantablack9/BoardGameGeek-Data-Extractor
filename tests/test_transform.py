"""Tests for transform module."""

from bgg_extractor.schemas import ThingItem, UserSchema
from bgg_extractor.transform import model_to_dict, models_to_list


def test_model_to_dict():
    """Test converting a single model to dict."""
    user = UserSchema(id=123, name="testuser")
    result = model_to_dict(user)
    assert isinstance(result, dict)
    assert result["id"] == 123
    assert result["name"] == "testuser"


def test_models_to_list():
    """Test converting a list of models to list of dicts."""
    items = [
        ThingItem(id=1, name="Game1", type="boardgame"),
        ThingItem(id=2, name="Game2", type="boardgame"),
    ]
    result = models_to_list(items)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["name"] == "Game2"
