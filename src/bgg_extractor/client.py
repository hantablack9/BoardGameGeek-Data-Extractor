"""
BGG XMLAPI2 client implementation using httpx for async requests.

"""

import asyncio
import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv

from bgg_extractor.schemas import CollectionSchema, FamilySchema, PlaysSchema, SearchSchema, ThingSchema, UserSchema

load_dotenv()


class BGGClient:
    """Async BGG XMLAPI2 client.

    Handles throttling, retries for 202 responses, and authentication.

    Attributes:
        BASE_URL: Default base URL for BGG XMLAPI2.
        DEFAULT_WAIT_SECONDS: Default minimum delay between requests.
        DEFAULT_TIMEOUT: Default request timeout in seconds.
        DEFAULT_MAX_POLL: Default maximum number of poll attempts for 202 responses.
    """

    BASE_URL: str = "https://api.geekdo.com/xmlapi2"
    DEFAULT_WAIT_SECONDS: float = 2.0
    DEFAULT_TIMEOUT: int = 30
    DEFAULT_MAX_POLL: int = 12

    def __init__(
        self,
        base_url: str = BASE_URL,
        min_delay: float = DEFAULT_WAIT_SECONDS,
        timeout: int = DEFAULT_TIMEOUT,
        max_poll_attempts: int = DEFAULT_MAX_POLL,
        token: str | None = None,
    ):
        """Initialize the BGGClient.

        Args:
            base_url: Base URL for the API.
            min_delay: Minimum seconds to wait between requests to respect rate limits.
            timeout: Request timeout in seconds.
            max_poll_attempts: Max attempts to poll when receiving a 202 response.
            token: Optional BGG API token (Bearer). If not provided, checks BGG_API_TOKEN env var.
        """
        self.base_url = base_url.rstrip("/")
        self.min_delay = float(min_delay)
        self.timeout = int(timeout)
        self.max_poll_attempts = int(max_poll_attempts)
        self.token = token or os.getenv("BGG_API_TOKEN")
        if not self.token:
            raise ValueError("BGG_API_TOKEN is required. Please set it in your environment or pass it to the client.")

        self._last_request_ts = 0.0
        self._lock = asyncio.Lock()

        # We'll use a single client for the session, but it should be managed carefully.
        # For simplicity in this design, we'll create a client per request or manage a lifecycle.
        # Ideally, the user should use a context manager, but we'll keep it simple for now
        # and instantiate a client internally or allow passing one.
        # To support "fast extraction", we'll use an internal client that persists if possible,
        # or just use `httpx.AsyncClient` context in methods.
        # Given the usage pattern, let's use a persistent client if used as a context manager,
        # otherwise create one-off.
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BGGClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        if self.token:
            self._client.headers.update({"Authorization": f"Bearer {self.token}"})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an httpx.AsyncClient."""
        if self._client:
            return self._client
        # If not in context manager, create a temporary one (not ideal for connection pooling but safe)
        # For better performance, users should use `async with BGGClient() ...`
        client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        client.headers.update({"User-Agent": "BGG-Extractor/1.0.0"})
        if self.token:
            client.headers.update({"Authorization": f"Bearer {self.token}"})
        return client

    async def _throttle(self) -> None:
        """Enforce minimum delay between requests."""
        async with self._lock:
            elapsed = time.time() - self._last_request_ts
            if elapsed < self.min_delay:
                await asyncio.sleep(self.min_delay - elapsed)
            self._last_request_ts = time.time()

    async def _request_xml(self, path: str, params: dict[str, Any]) -> str:
        """Make an async GET request, handling throttling and 202 retries.

        Args:
            path: API endpoint path (e.g., 'thing').
            params: Query parameters.

        Returns:
            The raw XML response string.

        Raises:
            RuntimeError: If the API returns an error or times out polling.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        attempts = 0

        # If we created a temp client, we must close it.
        # If self._client is set, we use it and don't close it.
        client = await self._get_client()
        should_close = self._client is None

        try:
            while True:
                await self._throttle()
                resp = await client.get(url, params=params)

                if resp.status_code == 200:
                    return resp.text

                if resp.status_code == 202:
                    attempts += 1
                    if attempts >= self.max_poll_attempts:
                        raise RuntimeError(f"BGG queued too long: {path} params={params}")

                    # Exponential backoff: min_delay * (1.5 ^ attempts)
                    # e.g., 2.0, 3.0, 4.5, 6.75...
                    backoff = self.min_delay * (1.5 ** (attempts - 1))
                    await asyncio.sleep(backoff)
                    continue

                raise RuntimeError(f"BGG API returned {resp.status_code}: {resp.text}")
        finally:
            if should_close:
                await client.aclose()

    async def get_user(
        self,
        name: str,
        buddies: bool = False,
        guilds: bool = False,
        hot: bool = False,
        top: bool = False,
        domain: str = "boardgame",
        page: int = 1,
        **kwargs,
    ) -> UserSchema:
        """Fetch user details.

        Args:
            name: The username.
            buddies: Include buddies list.
            guilds: Include guilds list.
            hot: Include hot list.
            top: Include top list.
            domain: Domain for hot/top lists (boardgame, rpg, videogame).
            page: Page number for buddies/guilds.
            **kwargs: Additional parameters.

        Returns:
            A UserSchema object.
        """
        params = {"name": name}
        if buddies:
            params["buddies"] = 1
        if guilds:
            params["guilds"] = 1
        if hot:
            params["hot"] = 1
        if top:
            params["top"] = 1
        if domain:
            params["domain"] = domain
        if page:
            params["page"] = page
        params.update(kwargs)
        xml = await self._request_xml("user", params)
        return UserSchema.parse_xml(xml)

    async def get_collection(
        self,
        username: str,
        version: bool = False,
        subtype: str = "boardgame",
        excludesubtype: str | None = None,
        stats: bool = True,
        brief: bool = False,
        showprivate: bool = False,
        minrating: float | None = None,
        rating: float | None = None,
        minbggrating: float | None = None,
        bggrating: float | None = None,
        minplays: int | None = None,
        maxplays: int | None = None,
        collectionid: int | None = None,
        modifiedsince: str | None = None,
        **kwargs,
    ) -> CollectionSchema:
        """Fetch a user's collection.

        Args:
            username: The username.
            version: Include version info.
            subtype: Item subtype (boardgame, boardgameexpansion, etc.).
            excludesubtype: Subtype to exclude.
            stats: Include ratings and stats.
            brief: Return abbreviated results.
            showprivate: Include private info.
            minrating: Filter by min user rating.
            rating: Filter by exact user rating.
            minbggrating: Filter by min BGG rating.
            bggrating: Filter by exact BGG rating.
            minplays: Filter by min plays.
            maxplays: Filter by max plays.
            collectionid: Restrict to specific collection ID.
            modifiedsince: Return items modified since date (YY-MM-DD or YY-MM-DD%20HH:MM:SS).
            **kwargs: Additional parameters.

        Returns:
            A CollectionSchema object.
        """
        params = {"username": username}
        if version:
            params["version"] = 1
        if subtype:
            params["subtype"] = subtype
        if excludesubtype:
            params["excludesubtype"] = excludesubtype
        if stats:
            params["stats"] = 1
        if brief:
            params["brief"] = 1
        if showprivate:
            params["showprivate"] = 1
        if minrating is not None:
            params["minrating"] = minrating
        if rating is not None:
            params["rating"] = rating
        if minbggrating is not None:
            params["minbggrating"] = minbggrating
        if bggrating is not None:
            params["bggrating"] = bggrating
        if minplays is not None:
            params["minplays"] = minplays
        if maxplays is not None:
            params["maxplays"] = maxplays
        if collectionid is not None:
            params["collectionid"] = collectionid
        if modifiedsince:
            params["modifiedsince"] = modifiedsince
        params.update(kwargs)
        xml = await self._request_xml("collection", params)
        return CollectionSchema.parse_xml(xml)

    async def get_thing(
        self,
        ids: list[int],
        thing_type: str | None = None,
        versions: bool = False,
        videos: bool = False,
        stats: bool = True,
        historical: bool = False,
        marketplace: bool = False,
        comments: bool = False,
        ratingcomments: bool = False,
        page: int = 1,
        pagesize: int = 100,
        **kwargs,
    ) -> ThingSchema:
        """Fetch details for specific things (games).

        Args:
            ids: List of BGG thing IDs.
            thing_type: Filter by item type.
            versions: Include version info.
            videos: Include videos.
            stats: Include ranking and rating stats.
            historical: Include historical data.
            marketplace: Include marketplace data.
            comments: Include comments.
            ratingcomments: Include comments with ratings.
            page: Page number for comments.
            pagesize: Page size for comments (10-100).
            **kwargs: Additional parameters.

        Returns:
            A ThingSchema object.
        """
        if not ids:
            raise ValueError("ids list must not be empty")
        params = {"id": ",".join(str(i) for i in ids)}
        if thing_type:
            params["type"] = thing_type
        if versions:
            params["versions"] = 1
        if videos:
            params["videos"] = 1
        if stats:
            params["stats"] = 1
        if historical:
            params["historical"] = 1
        if marketplace:
            params["marketplace"] = 1
        if comments:
            params["comments"] = 1
        if ratingcomments:
            params["ratingcomments"] = 1
        if page:
            params["page"] = page
        if pagesize:
            params["pagesize"] = pagesize
        params.update(kwargs)
        xml = await self._request_xml("thing", params)
        return ThingSchema.parse_xml(xml)

    async def search(
        self,
        query: str,
        thing_type: str | None = None,
        exact: bool = False,
        **kwargs,
    ) -> SearchSchema:
        """Search for items.

        Args:
            query: The search query string.
            thing_type: Filter by item type.
            exact: Exact match only.
            **kwargs: Additional parameters.

        Returns:
            A SearchSchema object.
        """
        params = {"query": query}
        if thing_type:
            params["type"] = thing_type
        if exact:
            params["exact"] = 1
        params.update(kwargs)
        xml = await self._request_xml("search", params)
        return SearchSchema.parse_xml(xml)

    async def get_plays(
        self,
        username: str | None = None,
        thing_id: int | None = None,
        thing_type: str | None = None,
        mindate: str | None = None,
        maxdate: str | None = None,
        subtype: str = "boardgame",
        page: int = 1,
        **kwargs,
    ) -> PlaysSchema:
        """Fetch plays data.

        Args:
            username: Username to fetch plays for.
            thing_id: ID of the item to fetch plays for.
            thing_type: Type of item (thing, family).
            mindate: Min date (YYYY-MM-DD).
            maxdate: Max date (YYYY-MM-DD).
            subtype: Subtype filter.
            page: Page number.
            **kwargs: Additional parameters.

        Returns:
            A PlaysSchema object.
        """
        params = {}
        if username:
            params["username"] = username
        if thing_id:
            params["id"] = thing_id
        if thing_type:
            params["type"] = thing_type
        if mindate:
            params["mindate"] = mindate
        if maxdate:
            params["maxdate"] = maxdate
        if subtype:
            params["subtype"] = subtype
        if page:
            params["page"] = page

        if not params.get("username") and not (params.get("id") and params.get("type")):
            raise ValueError("username OR (id and type) required for plays")

        params.update(kwargs)
        xml = await self._request_xml("plays", params)
        return PlaysSchema.parse_xml(xml)

    async def get_family(
        self,
        ids: list[int],
        family_type: str | None = None,
        **kwargs,
    ) -> FamilySchema:
        """Fetch details for specific families.

        Args:
            ids: List of BGG family IDs.
            family_type: Filter by family type (rpg, boardgamefamily, etc.).
            **kwargs: Additional parameters.

        Returns:
            A FamilySchema object.
        """
        if not ids:
            raise ValueError("ids list must not be empty")
        params = {"id": ",".join(str(i) for i in ids)}
        if family_type:
            params["type"] = family_type
        params.update(kwargs)
        xml = await self._request_xml("family", params)
        return FamilySchema.parse_xml(xml)


def run_sync(coro):
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def search(query: str, **kwargs) -> SearchSchema:
    """Synchronous wrapper for search."""

    async def _run():
        async with BGGClient() as client:
            return await client.search(query, **kwargs)

    return run_sync(_run())


def get_things(ids: list[int], **kwargs) -> ThingSchema:
    """Synchronous wrapper for get_thing."""

    async def _run():
        async with BGGClient() as client:
            return await client.get_thing(ids, **kwargs)

    return run_sync(_run())


def get_collection(username: str, **kwargs) -> CollectionSchema:
    """Synchronous wrapper for get_collection."""

    async def _run():
        async with BGGClient() as client:
            return await client.get_collection(username, **kwargs)

    return run_sync(_run())


def get_plays(username: str | None = None, thing_id: int | None = None, **kwargs) -> PlaysSchema:
    """Synchronous wrapper for get_plays."""

    async def _run():
        async with BGGClient() as client:
            return await client.get_plays(username=username, thing_id=thing_id, **kwargs)

    return run_sync(_run())


def get_family(ids: list[int], **kwargs) -> FamilySchema:
    """Synchronous wrapper for get_family."""

    async def _run():
        async with BGGClient() as client:
            return await client.get_family(ids, **kwargs)

    return run_sync(_run())


def get_user(name: str, **kwargs) -> UserSchema:
    """Synchronous wrapper for get_user."""

    async def _run():
        async with BGGClient() as client:
            return await client.get_user(name, **kwargs)

    return run_sync(_run())
