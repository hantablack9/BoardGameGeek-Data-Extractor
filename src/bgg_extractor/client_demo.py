"""
BGG XMLAPI2 lightweight client.

Features:
- get_user, get_collection, get_thing, search, get_plays
- Handles 202 "queued" responses by polling until completion (with capped retries)
- Respects a default minimum delay between requests (BGG recommends ~5 seconds)
- Parses minimal fields from returned XML into Python dict/list structures
"""

import os
import time
import xml.etree.ElementTree as ET
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env into environment
token = os.getenv("BGG_API_TOKEN")

BASE = "https://boardgamegeek.com/xmlapi2"
DEFAULT_WAIT_SECONDS = 5.0
DEFAULT_TIMEOUT = 30.0
MAX_POLL_ATTEMPTS = 12  # 12 * 5s = ~60s max wait for 202 -> 200


class BGGClient:
    def __init__(
        self,
        base_url: str = BASE,
        min_delay: float = DEFAULT_WAIT_SECONDS,
        timeout: float = DEFAULT_TIMEOUT,
        max_poll_attempts: int = MAX_POLL_ATTEMPTS,
        bearer_token: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.min_delay = float(min_delay)
        self.timeout = float(timeout)
        self.max_poll_attempts = int(max_poll_attempts)
        self._session = requests.Session()
        self._last_request_ts = 0.0
        if bearer_token:
            # official requirement: "Authorization: Bearer <token>"
            self._session.headers.update({"Authorization": f"Bearer {bearer_token}"})

    def _throttle(self):
        elapsed = time.time() - self._last_request_ts
        if elapsed < self.min_delay:
            to_sleep = self.min_delay - elapsed
            time.sleep(to_sleep)

    def _request_xml(self, path: str, params: dict[str, Any]) -> str:
        """
        GET request that:
        - respects throttle (min_delay)
        - polls on 202 responses until 200 or until attempts exhausted
        Returns XML text on success (200), raises RuntimeError on failure.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        attempts = 0
        while True:
            self._throttle()
            self._last_request_ts = time.time()
            try:
                resp = self._session.get(url, params=params, timeout=self.timeout)
            except requests.RequestException as e:
                raise RuntimeError(f"Network error while requesting {url}: {e}") from e

            if resp.status_code == 200:
                return resp.text
            elif resp.status_code == 202:
                # queued; poll until ready
                attempts += 1
                if attempts >= self.max_poll_attempts:
                    raise RuntimeError(f"BGG API still queued after {attempts} attempts (path={path}, params={params})")
                # exponential-ish backoff but still respect min_delay
                # sleep at least min_delay (BGG recommends ~5s between requests)
                time.sleep(self.min_delay)
                continue
            else:
                # treat 500/503 as transient too, optionally allow caller to retry
                raise RuntimeError(f"BGG API returned status {resp.status_code} for {url} with params {params}")

    # --- high-level API methods ---

    def get_user(
        self,
        name: str,
        buddies: bool = False,
        guilds: bool = False,
        hot: bool = False,
        top: bool = False,
        domain: str | None = None,
        page: int | None = None,
    ) -> dict:
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
        xml = self._request_xml("user", params)
        return self._parse_user(xml)

    def get_collection(
        self,
        username: str,
        version: int | None = None,
        subtype: str | None = None,
        excludesubtype: str | None = None,
        stats: bool = False,
        brief: bool = False,
        page: int | None = None,
        showprivate: bool = False,
    ) -> dict:
        params = {"username": username}
        if version:
            params["version"] = version
        if subtype:
            params["subtype"] = subtype
        if excludesubtype:
            params["excludesubtype"] = excludesubtype
        if stats:
            params["stats"] = 1
        if brief:
            params["brief"] = 1
        if page:
            params["page"] = page
        if showprivate:
            params["showprivate"] = 1
        xml = self._request_xml("collection", params)
        return self._parse_collection(xml)

    def get_thing(
        self,
        ids: list[int],
        type_: str | None = None,
        versions: bool = False,
        videos: bool = False,
        stats: bool = False,
    ) -> dict:
        params = {"id": ",".join(str(i) for i in ids)}
        if type_:
            params["type"] = type_
        if versions:
            params["versions"] = 1
        if videos:
            params["videos"] = 1
        if stats:
            params["stats"] = 1
        xml = self._request_xml("thing", params)
        return self._parse_thing(xml)

    def search(self, query: str, type_: str | None = None, exact: bool = False) -> dict:
        params = {"query": query}
        if type_:
            params["type"] = type_
        if exact:
            params["exact"] = 1
        xml = self._request_xml("search", params)
        return self._parse_search(xml)

    def get_plays(
        self,
        username: str | None = None,
        id_: int | None = None,
        type_: str | None = None,
        min_date: str | None = None,
        max_date: str | None = None,
        page: int | None = None,
    ) -> dict:
        params = {}
        if username:
            params["username"] = username
        if id_:
            params["id"] = id_
        if type_:
            params["type"] = type_
        if min_date:
            params["mindate"] = min_date
        if max_date:
            params["maxdate"] = max_date
        if page:
            params["page"] = page
        if not params:
            raise ValueError("Must supply username or id/type to get plays")
        xml = self._request_xml("plays", params)
        return self._parse_plays(xml)

    # --- minimal XML parsing utilities (expand as you need) ---

    def _parse_user(self, xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        # <user id="..." name="..." ...>
        usr = root.find("user")
        if usr is None:
            return {}
        out = {
            "id": usr.attrib.get("id"),
            "name": usr.attrib.get("name"),
            "firstname": usr.attrib.get("firstname"),
            "lastname": usr.attrib.get("lastname"),
            "avatar": usr.attrib.get("avatar"),
            "registered": usr.attrib.get("registered"),
        }
        # optionally extract top/hot lists
        hot = usr.find("hot")
        if hot is not None:
            out["hot"] = [item.attrib for item in hot.findall("item")]
        top = usr.find("top")
        if top is not None:
            out["top"] = [item.attrib for item in top.findall("item")]
        return out

    def _parse_collection(self, xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        collection = {"items": []}
        for item in root.findall("item"):
            it = {
                "objectid": item.attrib.get("objectid"),
                "subtype": item.attrib.get("subtype"),
                "collid": item.attrib.get("collid"),
            }
            name_node = item.find("name")
            if name_node is not None:
                it["name"] = name_node.attrib.get("value")
            stats = item.find("stats")
            if stats is not None:
                it["rating"] = stats.attrib.get("rating")
            collection["items"].append(it)
        return collection

    def _parse_thing(self, xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        things = []
        for item in root.findall("item"):
            t = {
                "id": item.attrib.get("id"),
                "type": item.attrib.get("type"),
            }
            name = item.find("name")
            if name is not None:
                t["name"] = name.attrib.get("value")
            year = item.find("yearpublished")
            if year is not None:
                t["yearpublished"] = year.attrib.get("value")
            stats = item.find("statistics")
            if stats is not None:
                ratings = stats.find("ratings")
                if ratings is not None:
                    try:
                        t["usersrated"] = ratings.attrib.get("usersrated")
                        t["average"] = ratings.attrib.get("average")
                    except Exception:  # noqa: S110 - Expected failure for non-date values
                        pass
            things.append(t)
        return {"items": things}

    def _parse_search(self, xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall("item"):
            name_elem = item.find("name")
            items.append({
                "id": item.attrib.get("id"),
                "type": item.attrib.get("type"),
                "name": name_elem.attrib.get("value") if name_elem is not None else None,
            })
        return {"items": items}

    def _parse_plays(self, xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        plays = []
        for play in root.findall("play"):
            p = {
                "id": play.attrib.get("id"),
                "date": play.attrib.get("date"),
                "quantity": play.attrib.get("quantity"),
                "length": play.attrib.get("length"),
            }
            item = play.find("item")
            if item is not None:
                p["item"] = item.attrib
            plays.append(p)
        return {"plays": plays}


if __name__ == "__main__":
    bgg = BGGClient(bearer_token=token)
    user = bgg.get_thing(ids=list(range(1, 11)))
    print(user)
