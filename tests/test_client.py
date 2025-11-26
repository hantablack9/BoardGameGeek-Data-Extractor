"""Unit tests for BGGClient."""

import pytest
import respx
from httpx import Response

from bgg_extractor.client import BGGClient
from bgg_extractor.schemas import ThingSchema, UserSchema


@pytest.mark.asyncio
async def test_get_user_success():
    """Test get_user returns a valid UserSchema on 200 OK."""
    xml_response = """
    <user id="123" name="testuser" termsofuse="link">
        <firstname value="Test"/>
        <lastname value="User"/>
        <avatar value="http://example.com/avatar.jpg"/>
        <yearregistered value="2020"/>
        <lastlogin value="2023-01-01"/>
        <stateorprovince value="WA"/>
        <country value="USA"/>
        <webaddress value=""/>
        <xboxaccount value=""/>
        <wiiaccount value=""/>
        <psnaccount value=""/>
        <battlenetaccount value=""/>
        <steamaccount value=""/>
        <traderating value="0"/>
    </user>
    """
    async with respx.mock:
        respx.get(url__startswith="https://api.geekdo.com/xmlapi2/user").mock(
            return_value=Response(200, text=xml_response)
        )

        async with BGGClient() as client:
            user = await client.get_user("testuser")
            assert isinstance(user, UserSchema)
            assert user.id == 123
            assert user.name == "testuser"
            assert user.firstname == "Test"


@pytest.mark.asyncio
async def test_get_thing_success():
    """Test get_thing returns a valid ThingSchema."""
    xml_response = """
    <items termsofuse="link">
        <item type="boardgame" id="1">
            <name type="primary" sortindex="1" value="Die Macher"/>
            <yearpublished value="1986"/>
        </item>
    </items>
    """
    async with respx.mock:
        respx.get(url__startswith="https://api.geekdo.com/xmlapi2/thing").mock(
            return_value=Response(200, text=xml_response)
        )

        async with BGGClient() as client:
            things = await client.get_thing([1])
            assert isinstance(things, ThingSchema)
            assert len(things.items) == 1
            assert things.items[0].id == 1
            assert things.items[0].name == "Die Macher"


@pytest.mark.asyncio
async def test_retry_on_202():
    """Test that the client retries on 202 Accepted responses."""
    xml_response = """<items><item id="1"><name value="Game"/></item></items>"""

    async with respx.mock:
        route = respx.get(url__startswith="https://api.geekdo.com/xmlapi2/thing")
        route.side_effect = [
            Response(202, text="Queued"),
            Response(202, text="Queued"),
            Response(200, text=xml_response),
        ]

        # Use a very short delay for testing
        async with BGGClient(min_delay=0.01) as client:
            things = await client.get_thing([1])
            assert len(things.items) == 1
            assert route.call_count == 3


@pytest.mark.asyncio
async def test_max_retries_exceeded():
    """Test that RuntimeError is raised when max poll attempts are exceeded."""
    async with respx.mock:
        respx.get(url__startswith="https://api.geekdo.com/xmlapi2/thing").mock(
            return_value=Response(202, text="Queued")
        )

        async with BGGClient(min_delay=0.01, max_poll_attempts=2) as client:
            with pytest.raises(RuntimeError, match="BGG queued too long"):
                await client.get_thing([1])
