import pytest
from pydantic import ValidationError

from bgg_extractor.schemas import ThingItem


def test_thing_item_valid_type():
    """Test that ThingItem accepts valid types."""
    item = ThingItem(type="boardgame")
    assert item.type == "boardgame"

    item = ThingItem(type="rpgitem")
    assert item.type == "rpgitem"


def test_thing_item_invalid_type():
    """Test that ThingItem rejects invalid types."""
    with pytest.raises(ValidationError):
        ThingItem(type="invalid_type")
