import pytest
from dotenv import load_dotenv
from tests.conftest import skip_if_no_real_token

from bgg_extractor.client import BGGClient
from bgg_extractor.schemas import SearchSchema, ThingSchema, UserSchema

load_dotenv()


@skip_if_no_real_token
@pytest.mark.asyncio
async def test_integration_get_thing():
    """Integration test for get_thing against real API."""
    async with BGGClient() as client:
        # Fetch "Catan" (ID 13)
        things = await client.get_thing([13])
        assert isinstance(things, ThingSchema)
        assert len(things.items) == 1
        item = things.items[0]
        assert item.id == 13
        assert item.name == "CATAN"
        assert item.type == "boardgame"


@skip_if_no_real_token
@pytest.mark.asyncio
async def test_integration_get_user():
    """Integration test for get_user against real API."""
    async with BGGClient() as client:
        # Fetch a known user, e.g., "BoardGameGeek" (admin) or a stable user
        # Fetch a known user, e.g., "BoardGameGeek" (admin) or a stable user
        user = await client.get_user("BoardGameGeek")
        assert isinstance(user, UserSchema)
        assert user.name is not None  # Type narrowing for type checker
        assert user.name.lower() == "boardgamegeek"
        assert user.id is not None


@skip_if_no_real_token
@pytest.mark.asyncio
async def test_integration_search():
    """Integration test for search against real API."""
    async with BGGClient() as client:
        # Search for "Catan"
        search_results = await client.search("Catan", type="boardgame")
        assert isinstance(search_results, SearchSchema)
        assert len(search_results.items) > 0

        # Verify at least one result is Catan (ID 13)
        found = False
        for item in search_results.items:
            if item.id == 13:
                found = True
                break
        assert found
