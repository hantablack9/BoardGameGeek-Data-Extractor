"""Unit tests for schemas and XML parsing."""

from bgg_extractor.schemas import CollectionSchema, PlaysSchema, ThingSchema, UserSchema


def test_parse_thing_xml():
    """Test parsing of a Thing XML."""
    xml = """
    <items>
        <item type="boardgame" id="1">
            <name value="Die Macher"/>
            <yearpublished value="1986"/>
            <statistics>
                <ratings usersrated="5000" average="7.6"/>
            </statistics>
        </item>
    </items>
    """
    schema = ThingSchema.parse_xml(xml)
    assert len(schema.items) == 1
    item = schema.items[0]
    assert item.id == 1
    assert item.name == "Die Macher"
    assert item.yearpublished == 1986
    assert item.usersrated == 5000
    assert item.average == 7.6


def test_parse_user_xml():
    """Test parsing of a User XML."""
    xml = """
    <user id="123" name="testuser">
        <firstname value="Test"/>
        <lastname value="User"/>
        <avatar value="http://example.com/avatar.jpg"/>
        <yearregistered value="2020"/>
    </user>
    """
    schema = UserSchema.parse_xml(xml)
    assert schema.id == 123
    assert schema.name == "testuser"
    assert schema.firstname == "Test"
    assert schema.registered == "2020"


def test_parse_collection_xml():
    """Test parsing of a Collection XML."""
    xml = """
    <items>
        <item objectid="1" subtype="boardgame" collid="10">
            <name value="Die Macher"/>
            <stats rating="8.0"/>
        </item>
    </items>
    """
    schema = CollectionSchema.parse_xml(xml)
    assert len(schema.items) == 1
    item = schema.items[0]
    assert item.objectid == 1
    assert item.name == "Die Macher"
    assert item.rating == 8.0


def test_parse_plays_xml():
    """Test parsing of a Plays XML."""
    xml = """
    <plays>
        <play id="100" date="2023-01-01" quantity="1" length="60">
            <item name="Die Macher" objectid="1"/>
        </play>
    </plays>
    """
    schema = PlaysSchema.parse_xml(xml)
    assert len(schema.plays) == 1
    play = schema.plays[0]
    assert play.id == 100
    assert play.date == "2023-01-01"
    assert play.quantity == 1
    assert play.length == 60
    assert play.item is not None  # Type narrowing for type checker
    assert play.item["name"] == "Die Macher"
