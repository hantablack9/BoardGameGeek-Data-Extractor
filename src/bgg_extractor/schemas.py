"""Pydantic schemas and XML parsing helpers for BGG API responses.

This module defines the data models for various BGG API entities (Thing, User, Collection, Plays)
and provides XML parsing logic to convert raw API responses into typed Pydantic objects.
"""

import xml.etree.ElementTree as ET
from typing import Any, Literal, cast

from pydantic import BaseModel

ThingType = Literal[
    "boardgame",
    "boardgameexpansion",
    "boardgameaccessory",
    "videogame",
    "rpgitem",
    "rpgissue",
]


class ThingItem(BaseModel):
    """Represents a single board game or item from the 'thing' endpoint.

    Attributes:
        id: The unique BGG ID of the item.
        type: The type of item (e.g., 'boardgame', 'boardgameexpansion').
        name: The primary name of the item.
        yearpublished: The year the item was published.
        usersrated: The number of users who have rated this item.
        average: The average user rating (1-10 scale).
    """

    id: int | None = None
    type: ThingType | None = None
    name: str | None = None
    description: str | None = None
    yearpublished: int | None = None
    minplayers: int | None = None
    maxplayers: int | None = None
    playingtime: int | None = None
    minage: int | None = None
    usersrated: int | None = None
    average: float | None = None
    rank: int | None = None
    categories: list[str] = []
    mechanics: list[str] = []
    designers: list[str] = []
    artists: list[str] = []
    publishers: list[str] = []


class ThingSchema(BaseModel):
    """Container for a list of ThingItems parsed from the 'thing' endpoint.

    Attributes:
        items: A list of ThingItem objects.
    """

    items: list[ThingItem] = []

    @classmethod
    def parse_xml(cls, xml_text: str) -> "ThingSchema":
        """Parses XML response from the 'thing' endpoint.

        Args:
            xml_text: The raw XML string from the API.

        Returns:
            A ThingSchema instance containing the parsed items.
        """
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall("item"):
            item_id = item.attrib.get("id")

            # Helper to get value from simple tag
            def get_val(tag: str, convert=str) -> Any | None:
                node = item.find(tag)
                if node is not None:
                    val = node.attrib.get("value")
                    if val:
                        try:
                            return convert(val)
                        except (ValueError, TypeError):
                            return None
                return None

            # Helper to get text content
            def get_text(tag: str) -> str | None:
                node = item.find(tag)
                return node.text if node is not None else None

            # Helper to get list of values from links
            def get_links(link_type: str) -> list[str]:
                return [
                    val
                    for link in item.findall("link")
                    if link.attrib.get("type") == link_type and (val := link.attrib.get("value")) is not None
                ]

            usersrated = None
            average = None
            rank = None
            stats = item.find("statistics")
            if stats is not None:
                ratings = stats.find("ratings")
                if ratings is not None:
                    usersrated = ratings.attrib.get("usersrated")
                    average = ratings.attrib.get("average")
                    ranks = ratings.find("ranks")
                    if ranks is not None:
                        # Get the main boardgame rank (id=1)
                        bg_rank = ranks.find("rank[@id='1']")
                        if bg_rank is not None:
                            rank_val = bg_rank.attrib.get("value")
                            if rank_val and rank_val != "Not Ranked":
                                rank = int(rank_val)

            items.append(
                ThingItem(
                    id=int(item_id) if item_id else None,
                    type=cast(ThingType, item.attrib.get("type"))
                    if item.attrib.get("type")
                    in ["boardgame", "boardgameexpansion", "boardgameaccessory", "videogame", "rpgitem", "rpgissue"]
                    else None,
                    name=get_val("name"),  # Primary name usually has type="primary" but value attribute is standard
                    description=get_text("description"),
                    yearpublished=get_val("yearpublished", int),
                    minplayers=get_val("minplayers", int),
                    maxplayers=get_val("maxplayers", int),
                    playingtime=get_val("playingtime", int),
                    minage=get_val("minage", int),
                    usersrated=int(usersrated) if usersrated else None,
                    average=float(average) if average else None,
                    rank=rank,
                    categories=get_links("boardgamecategory"),
                    mechanics=get_links("boardgamemechanic"),
                    designers=get_links("boardgamedesigner"),
                    artists=get_links("boardgameartist"),
                    publishers=get_links("boardgamepublisher"),
                )
            )
        return cls(items=items)


class UserSchema(BaseModel):
    """Represents a BGG user profile.

    Attributes:
        id: The user's unique ID.
        name: The user's username.
        firstname: The user's first name.
        lastname: The user's last name.
        avatar: URL to the user's avatar image.
        registered: The year (or date) the user registered.
    """

    id: int | None = None
    name: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    avatar: str | None = None
    registered: str | None = None
    buddies: list[dict[str, Any]] = []
    guilds: list[dict[str, Any]] = []
    hot: list[dict[str, Any]] = []
    top: list[dict[str, Any]] = []

    @classmethod
    def parse_xml(cls, xml_text: str) -> "UserSchema":
        """Parses XML response from the 'user' endpoint.

        Args:
            xml_text: The raw XML string from the API.

        Returns:
            A UserSchema instance. Returns an empty schema if the user tag is missing.
        """
        root = ET.fromstring(xml_text)
        if root.tag == "user":
            usr = root
        else:
            usr = root.find("user")

        if usr is None:
            return cls()

        def get_val(tag_name: str) -> str | None:
            tag = usr.find(tag_name)
            return tag.attrib.get("value") if tag is not None else None

        def get_list(tag_name: str) -> list[dict[str, Any]]:
            node = usr.find(tag_name)
            if node is not None:
                return [item.attrib for item in node.findall("item") or node.findall("buddy") or node.findall("guild")]
            return []

        return cls(
            id=int(usr.attrib.get("id")) if usr.attrib.get("id") else None,
            name=usr.attrib.get("name"),
            firstname=get_val("firstname"),
            lastname=get_val("lastname"),
            avatar=get_val("avatar"),
            registered=get_val("yearregistered"),
            buddies=get_list("buddies"),
            guilds=get_list("guilds"),
            hot=get_list("hot"),
            top=get_list("top"),
        )


class CollectionItem(BaseModel):
    """Represents a single item in a user's collection.

    Attributes:
        objectid: The BGG ID of the item.
        subtype: The subtype of the item (e.g., 'boardgame').
        collid: The unique ID of this collection entry.
        name: The name of the item.
        rating: The user's rating for this item, if available.
        status: Dictionary of status flags (owned, wanted, etc.).
        comment: User's comment on the item.
    """

    objectid: int | None = None
    subtype: str | None = None
    collid: int | None = None
    name: str | None = None
    rating: float | None = None
    status: dict[str, Any] = {}
    comment: str | None = None


class CollectionSchema(BaseModel):
    """Container for a list of CollectionItems parsed from the 'collection' endpoint.

    Attributes:
        items: A list of CollectionItem objects.
    """

    items: list[CollectionItem] = []

    @classmethod
    def parse_xml(cls, xml_text: str) -> "CollectionSchema":
        """Parses XML response from the 'collection' endpoint.

        Args:
            xml_text: The raw XML string from the API.

        Returns:
            A CollectionSchema instance containing the parsed items.
        """
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall("item"):
            name_node = item.find("name")
            stats = item.find("stats")
            status_node = item.find("status")
            comment_node = item.find("comment")

            rating = None
            if stats is not None:
                rating_node = stats.find("rating")
                if rating_node is not None:
                    val = rating_node.attrib.get("value")
                    if val and val != "N/A":
                        rating = val

            items.append(
                CollectionItem(
                    objectid=int(item.attrib.get("objectid")) if item.attrib.get("objectid") else None,
                    subtype=item.attrib.get("subtype"),
                    collid=int(item.attrib.get("collid")) if item.attrib.get("collid") else None,
                    name=name_node.text if name_node is not None else None,
                    rating=float(rating) if rating else None,
                    status=status_node.attrib if status_node is not None else {},
                    comment=comment_node.text if comment_node is not None else None,
                )
            )
        return cls(items=items)


class PlayItem(BaseModel):
    """Represents a single play record.

    Attributes:
        id: The unique ID of the play.
        date: The date of the play (YYYY-MM-DD).
        quantity: The number of times played.
        length: The duration of the play in minutes.
        location: Location where the play occurred.
        comment: Comments about the play.
        item: A dictionary containing details about the game played (name, id, etc.).
        players: List of players involved in the play.
    """

    id: int | None = None
    date: str | None = None
    quantity: int | None = None
    length: int | None = None
    location: str | None = None
    comment: str | None = None
    item: dict[str, Any] | None = None
    players: list[dict[str, Any]] = []


class PlaysSchema(BaseModel):
    """Container for a list of PlayItems parsed from the 'plays' endpoint.

    Attributes:
        plays: A list of PlayItem objects.
    """

    plays: list[PlayItem] = []

    @classmethod
    def parse_xml(cls, xml_text: str) -> "PlaysSchema":
        """Parses XML response from the 'plays' endpoint.

        Args:
            xml_text: The raw XML string from the API.

        Returns:
            A PlaysSchema instance containing the parsed plays.
        """
        root = ET.fromstring(xml_text)
        plays = []
        for p in root.findall("play"):
            players = []
            players_node = p.find("players")
            if players_node is not None:
                players = [pl.attrib for pl in players_node.findall("player")]

            comments_elem = p.find("comments")
            item_elem = p.find("item")
            plays.append(
                PlayItem(
                    id=int(p.attrib.get("id")) if p.attrib.get("id") else None,
                    date=p.attrib.get("date"),
                    quantity=int(p.attrib.get("quantity")) if p.attrib.get("quantity") else None,
                    length=int(p.attrib.get("length")) if p.attrib.get("length") else None,
                    location=p.attrib.get("location"),
                    comment=comments_elem.text if comments_elem is not None else None,
                    item=item_elem.attrib if item_elem is not None else None,
                    players=players,
                )
            )
        return cls(plays=plays)


class SearchQuery(BaseModel):
    """Schema for search parameters."""

    query: str
    types: list[ThingType] | None = None
    exact: bool = True

    @classmethod
    def from_query(cls, query: str) -> "SearchQuery":
        """Create a SearchQuery from a query string.

        Args:
            query: The search query. Spaces will be replaced with '+'.

        Returns:
            A SearchQuery instance.
        """
        import re

        query = re.sub(" ", "+", query)
        return cls(query=query)

    @classmethod
    def from_types(cls, query: str, types: list[ThingType]) -> "SearchQuery":
        """Create a SearchQuery from a query and a list of types.

        Args:
            query: The search query.
            types: A list of ThingTypes to filter by.

        Returns:
            A SearchQuery instance.
        """
        return cls(query=query, types=types)

    @property
    def search_string(self) -> str:
        """Generate the query string for the API.

        Returns:
            The formatted query string (e.g., "search?query=foo&type=boardgame&exact=1").
        """
        params = [f"query={self.query}"]

        if self.types:
            type_str = ",".join(self.types)
            params.append(f"type={type_str}")

        if self.exact:
            params.append("exact=1")

        return f"search?{'&'.join(params)}"


class SearchSchema(BaseModel):
    """Container for search results parsed from the 'search' endpoint.

    Attributes:
        items: A list of ThingItem objects found.
    """

    items: list[ThingItem] = []

    @classmethod
    def parse_xml(cls, xml_text: str) -> "SearchSchema":
        """Parses XML response from the 'search' endpoint.

        Args:
            xml_text: The raw XML string from the API.

        Returns:
            A SearchSchema instance containing the parsed items.
        """
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall("item"):
            item_id = item.attrib.get("id")
            name = item.find("name")
            year = item.find("yearpublished")

            # Search results don't usually have stats, but share the same basic structure
            items.append(
                ThingItem(
                    id=int(item_id) if item_id else None,
                    type=cast(ThingType, item.attrib.get("type"))
                    if item.attrib.get("type")
                    in ["boardgame", "boardgameexpansion", "boardgameaccessory", "videogame", "rpgitem", "rpgissue"]
                    else None,
                    name=name.attrib.get("value") if name is not None else None,
                    yearpublished=int(year.attrib.get("value"))
                    if year is not None and year.attrib.get("value")
                    else None,
                )
            )
        return cls(items=items)


class FamilyItem(BaseModel):
    """Represents a family item (e.g., RPG, Board Game Family).

    Attributes:
        id: The unique BGG ID of the family.
        type: The type of family.
        name: The name of the family.
        description: Description of the family.
    """

    id: int | None = None
    type: str | None = None
    name: str | None = None
    description: str | None = None


class FamilySchema(BaseModel):
    """Container for a list of FamilyItems parsed from the 'family' endpoint.

    Attributes:
        items: A list of FamilyItem objects.
    """

    items: list[FamilyItem] = []

    @classmethod
    def parse_xml(cls, xml_text: str) -> "FamilySchema":
        """Parses XML response from the 'family' endpoint.

        Args:
            xml_text: The raw XML string from the API.

        Returns:
            A FamilySchema instance containing the parsed items.
        """
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall("item"):
            item_id = item.attrib.get("id")
            name = item.find("name")
            desc = item.find("description")

            items.append(
                FamilyItem(
                    id=int(item_id) if item_id else None,
                    type=item.attrib.get("type"),
                    name=name.attrib.get("value") if name is not None else None,
                    description=desc.text if desc is not None else None,
                )
            )
        return cls(items=items)
