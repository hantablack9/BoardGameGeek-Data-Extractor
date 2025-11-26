from bgg_extractor.schemas import SearchQuery, SearchSchema


def test_search_query_basic():
    """Test basic SearchQuery creation."""
    s = SearchQuery(query="catan")
    assert s.query == "catan"
    assert s.types is None
    assert s.exact is True
    assert s.search_string == "search?query=catan&exact=1"


def test_search_query_from_query():
    """Test from_query factory method."""
    s = SearchQuery.from_query("ticket to ride")
    assert s.query == "ticket+to+ride"
    assert s.search_string == "search?query=ticket+to+ride&exact=1"


def test_search_query_with_types():
    """Test SearchQuery with types."""
    s = SearchQuery(query="pandemic", types=["boardgame", "boardgameexpansion"])
    assert s.types == ["boardgame", "boardgameexpansion"]
    expected = "search?query=pandemic&type=boardgame,boardgameexpansion&exact=1"
    assert s.search_string == expected


def test_search_query_no_exact():
    """Test SearchQuery with exact=False."""
    s = SearchQuery(query="monopoly", exact=False)
    assert s.exact is False
    assert s.search_string == "search?query=monopoly"


def test_search_query_from_types():
    """Test from_types factory method."""
    s = SearchQuery.from_types(query="gloomhaven", types=["boardgame"])
    assert s.query == "gloomhaven"
    assert s.types == ["boardgame"]
    assert s.search_string == "search?query=gloomhaven&type=boardgame&exact=1"


def test_search_schema_parse_xml():
    """Test parsing of Search XML."""
    xml = """
    <items total="2">
        <item type="boardgame" id="13">
            <name type="primary" value="Catan"/>
            <yearpublished value="1995"/>
        </item>
        <item type="boardgameexpansion" id="14">
            <name type="primary" value="Catan: Seafarers"/>
            <yearpublished value="1997"/>
        </item>
    </items>
    """
    schema = SearchSchema.parse_xml(xml)
    assert len(schema.items) == 2

    item1 = schema.items[0]
    assert item1.id == 13
    assert item1.type == "boardgame"
    assert item1.name == "Catan"
    assert item1.yearpublished == 1995

    item2 = schema.items[1]
    assert item2.id == 14
    assert item2.type == "boardgameexpansion"
    assert item2.name == "Catan: Seafarers"
    assert item2.yearpublished == 1997
