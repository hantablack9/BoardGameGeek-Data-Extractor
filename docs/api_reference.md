# BGG Extractor API Reference

Complete API reference for all modules and functions in the BGG Extractor library.

## Table of Contents
- [Client Functions](#client-functions)
- [Persistence Functions](#persistence-functions)
- [Transform Functions](#transform-functions)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Client Functions

### Synchronous API

High-level synchronous functions that handle async operations internally.

#### `search(query, **kwargs)`

Search for board games by name.

**Parameters:**
- `query` (str): Search query string
- `type` (str, optional): Filter by item type
- `exact` (bool, optional): Exact match only
- `**kwargs`: Additional BGG API parameters

**Returns:**
- `SearchSchema`: Search results containing list of items

**Example:**
```python
from bgg_extractor import search

results = search("Wingspan")
results = search("Pandemic", type="boardgame", exact=True)
```

---

#### `get_things(ids, **kwargs)`

Get detailed information about specific games.

**Parameters:**
- `ids` (list[int]): List of game IDs (max 20 per request)
- `type` (str, optional): Filter by thing type
- `stats` (bool, optional): Include ranking and rating stats (default: True)
- `versions` (bool, optional): Include version info
- `videos` (bool, optional): Include videos
- `historical` (bool, optional): Include historical data
- `marketplace` (bool, optional): Include marketplace data
- `comments` (bool, optional): Include comments
- `ratingcomments` (bool, optional): Include rating comments
- `page` (int, optional): Page number for comments
- `pagesize` (int, optional): Page size for comments (10-100)
- `**kwargs`: Additional BGG API parameters

**Returns:**
- `ThingSchema`: Game details containing list of items

**Example:**
```python
from bgg_extractor import get_things

# Get single game
game = get_things([174430], stats=True)

# Get multiple games
games = get_things([13, 174430, 266192], stats=True, videos=True)
```

---

#### `get_collection(username, **kwargs)`

Get a user's game collection.

**Parameters:**
- `username` (str): BGG username
- `version` (bool, optional): Include version info
- `subtype` (str, optional): Item subtype (default: "boardgame")
- `excludesubtype` (str, optional): Subtype to exclude
- `stats` (bool, optional): Include ratings and stats (default: True)
- `brief` (bool, optional): Return abbreviated results
- `showprivate` (bool, optional): Include private info
- `minrating` (float, optional): Filter by min user rating
- `rating` (float, optional): Filter by exact user rating
- `minbggrating` (float, optional): Filter by min BGG rating
- `bggrating` (float, optional): Filter by exact BGG rating
- `minplays` (int, optional): Filter by min plays
- `maxplays` (int, optional): Filter by max plays
- `collectionid` (int, optional): Restrict to specific collection ID
- `modifiedsince` (str, optional): Return items modified since date (YY-MM-DD)
- `**kwargs`: Additional BGG API parameters

**Returns:**
- `CollectionSchema`: Collection data containing list of items

**Example:**
```python
from bgg_extractor import get_collection

collection = get_collection("eekspider", stats=True)
owned_games = get_collection("username", stats=True, minrating=7)
```

---

#### `get_plays(username=None, **kwargs)`

Get play history for a user or game.

**Parameters:**
- `username` (str, optional): Username to fetch plays for
- `id` (int, optional): ID of the item to fetch plays for
- `type` (str, optional): Type of item (thing, family)
- `mindate` (str, optional): Min date (YYYY-MM-DD)
- `maxdate` (str, optional): Max date (YYYY-MM-DD)
- `subtype` (str, optional): Subtype filter (default: "boardgame")
- `page` (int, optional): Page number
- `**kwargs`: Additional BGG API parameters

**Returns:**
- `PlaysSchema`: Play data containing list of play items

**Example:**
```python
from bgg_extractor import get_plays

plays = get_plays(username="eekspider")
recent_plays = get_plays(username="eekspider", mindate="2024-01-01")
```

---

#### `get_user(name, **kwargs)`

Get user profile information.

**Parameters:**
- `name` (str): BGG username
- `buddies` (bool, optional): Include buddies list
- `guilds` (bool, optional): Include guilds list
- `hot` (bool, optional): Include hot list
- `top` (bool, optional): Include top list
- `domain` (str, optional): Domain for hot/top lists (default: "boardgame")
- `page` (int, optional): Page number for buddies/guilds
- `**kwargs`: Additional BGG API parameters

**Returns:**
- `UserSchema`: User profile data

**Example:**
```python
from bgg_extractor import get_user

user = get_user("eekspider")
user_with_top = get_user("eekspider", top=True, domain="boardgame")
```

---

#### `get_family(ids, **kwargs)`

Get details for specific game families.

**Parameters:**
- `ids` (list[int]): List of family IDs
- `type` (str, optional): Filter by family type
- `**kwargs`: Additional BGG API parameters

**Returns:**
- `FamilySchema`: Family data containing list of items

**Example:**
```python
from bgg_extractor import get_family

family = get_family([2651], type="boardgamefamily")
```

---

### Asynchronous API

Direct async client for advanced use cases.

#### `BGGClient`

Async context manager for BGG API operations.

**Constructor Parameters:**
- `base_url` (str): Base URL for the API (default: "https://api.geekdo.com/xmlapi2")
- `min_delay` (float): Minimum seconds between requests (default: 2.0)
- `timeout` (int): Request timeout in seconds (default: 30)
- `max_poll_attempts` (int): Max attempts to poll for 202 responses (default: 12)
- `token` (str, optional): BGG API token (reads from BGG_API_TOKEN env var if not provided)

**Methods:**
All methods are async and must be awaited. They have the same parameters as their synchronous counterparts.

- `async search(query, **kwargs) -> SearchSchema`
- `async get_thing(ids, **kwargs) -> ThingSchema`
- `async get_collection(username, **kwargs) -> CollectionSchema`
- `async get_plays(username=None, **kwargs) -> PlaysSchema`
- `async get_user(name, **kwargs) -> UserSchema`
- `async get_family(ids, **kwargs) -> FamilySchema`

**Example:**
```python
import asyncio
from bgg_extractor import BGGClient

async def fetch_data():
    async with BGGClient(token="your_token") as client:
        results = await client.search("Gloomhaven")
        games = await client.get_thing([174430], stats=True)
        return games

games = asyncio.run(fetch_data())
```

---

## Persistence Functions

### `save_json(data, filepath)`

Save data to JSON file.

**Parameters:**
- `data`: Data to save (list of Pydantic models or dicts)
- `filepath` (str): Output file path

**Example:**
```python
from bgg_extractor import get_things, save_json

games = get_things([13, 174430])
save_json(games.items, "games.json")
```

---

### `save_csv(data, filepath)`

Save data to CSV file.

**Parameters:**
- `data`: Data to save (list of Pydantic models or dicts)
- `filepath` (str): Output file path

**Example:**
```python
from bgg_extractor import get_things, save_csv

games = get_things([13, 174430])
save_csv(games.items, "games.csv")
```

---

## Transform Functions

### `model_to_dict(model)`

Convert a single Pydantic model to dictionary.

**Parameters:**
- `model` (BaseModel): Pydantic model instance

**Returns:**
- `dict`: Dictionary representation

**Example:**
```python
from bgg_extractor import get_things
from bgg_extractor.transform import model_to_dict

games = get_things([13])
game_dict = model_to_dict(games.items[0])
```

---

### `models_to_list(models)`

Convert a sequence of Pydantic models to list of dictionaries.

**Parameters:**
- `models` (Sequence[BaseModel]): Sequence of Pydantic models

**Returns:**
- `list[dict]`: List of dictionary representations

**Example:**
```python
from bgg_extractor import get_things
from bgg_extractor.transform import models_to_list
import pandas as pd

games = get_things([13, 174430, 266192])
games_dict = models_to_list(games.items)
df = pd.DataFrame(games_dict)
```

---

## Data Models

### SearchSchema

**Fields:**
- `total` (int): Total number of results
- `termsofuse` (str): Terms of use URL
- `items` (list[SearchItem]): List of search results

#### SearchItem
- `type` (str): Item type
- `id` (int): Item ID
- `name` (str): Item name
- `yearpublished` (int, optional): Year published

---

### ThingSchema

**Fields:**
- `termsofuse` (str): Terms of use URL
- `items` (list[ThingItem]): List of game details

#### ThingItem
- `id` (int): Game ID
- `type` (str): Game type
- `name` (str): Game name
- `description` (str, optional): Game description
- `yearpublished` (int, optional): Year published
- `minplayers` (int, optional): Minimum players
- `maxplayers` (int, optional): Maximum players
- `playingtime` (int, optional): Playing time in minutes
- `minage` (int, optional): Minimum recommended age
- `usersrated` (int, optional): Number of user ratings
- `average` (float, optional): Average rating
- `rank` (int, optional): BGG rank
- `categories` (list[str]): Game categories
- `mechanics` (list[str]): Game mechanics
- `designers` (list[str]): Game designers
- `artists` (list[str]): Game artists
- `publishers` (list[str]): Game publishers

---

### CollectionSchema

**Fields:**
- `totalitems` (int): Total items in collection
- `termsofuse` (str): Terms of use URL
- `pubdate` (str): Publication date
- `items` (list[CollectionItem]): List of collection items

#### CollectionItem
- `objecttype` (str): Object type
- `objectid` (int): Object ID
- `subtype` (str): Subtype
- `collid` (int): Collection ID
- `name` (str): Game name
- `yearpublished` (int, optional): Year published
- `image` (str, optional): Image URL
- `thumbnail` (str, optional): Thumbnail URL
- `status` (dict): Ownership status
- `numplays` (int): Number of plays

---

### PlaysSchema

**Fields:**
- `username` (str): Username
- `userid` (int): User ID
- `total` (int): Total plays
- `page` (int): Current page
- `termsofuse` (str): Terms of use URL
- `plays` (list[Play]): List of plays

#### Play
- `id` (int): Play ID
- `date` (str): Play date
- `quantity` (int): Quantity
- `length` (int): Play length in minutes
- `incomplete` (bool): Incomplete flag
- `nowinstats` (bool): Include in stats flag
- `location` (str, optional): Play location
- `item` (dict): Game information

---

### UserSchema

**Fields:**
- `id` (int): User ID
- `name` (str): Username
- `firstname` (str, optional): First name
- `lastname` (str, optional): Last name
- `avatar` (str, optional): Avatar URL
- `registered` (str): Registration date
- `buddies` (list): Buddies list
- `guilds` (list): Guilds list
- `hot` (list): Hot list
- `top` (list): Top list

---

## Error Handling

### Exceptions

The library raises standard Python exceptions:

- `ValueError`: Raised when BGG_API_TOKEN is not provided
- `RuntimeError`: Raised for BGG API errors (4xx, 5xx responses)
- `httpx.TimeoutException`: Raised on request timeout

### Example Error Handling

```python
from bgg_extractor import get_things

try:
    games = get_things([999999])  # Invalid ID
except RuntimeError as e:
    print(f"API Error: {e}")
except ValueError as e:
    print(f"Configuration Error: {e}")
```

### API Rate Limiting

The BGG API has the following limits:

- **Request limit**: 20 items per request for `get_things`
- **Rate limit**: Automatic 2-second delay between requests (configurable)
- **202 Responses**: API may queue requests; library retries automatically

**Handling 202 Responses:**

The library automatically polls for up to 12 attempts (configurable) with exponential backoff.

```python
from bgg_extractor import BGGClient

# Increase polling attempts
async with BGGClient(max_poll_attempts=20) as client:
    results = await client.search("Catan")
```

**Increasing Delay:**

```python
# Increase delay between requests to 5 seconds
async with BGGClient(min_delay=5.0) as client:
    results = await client.search("Catan")
```
