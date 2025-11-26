# BGG Extractor User Guide

Complete guide to using the BoardGameGeek Data Extractor library.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Python Library Usage](#python-library-usage)
- [Troubleshooting](#troubleshooting)

## Installation

### Via pip (when published to PyPI)
```bash
pip install bgg-extractor
```

### From source
```bash
git clone https://github.com/hantablack9/BoardGameGeek-Data-Extractor.git
cd BoardGameGeek-Data-Extractor
pip install -e .
```

### With uv (recommended)
```bash
uv add bgg-extractor
# or from local source
uv add ../BoardGameGeek-Data-Extractor
```

## Configuration

### BGG API Token (Required)

The BGG API token is **mandatory** for all operations. Set it up in one of three ways:

#### Option 1: Environment Variable
```bash
# Windows PowerShell
$env:BGG_API_TOKEN="your_token_here"

# Linux/Mac
export BGG_API_TOKEN="your_token_here"
```

#### Option 2: .env File (Recommended)
Create a `.env` file in your project root:
```
BGG_API_TOKEN=your_token_here
```

The library will automatically load this file.

#### Option 3: Pass Directly in Code
```python
from bgg_extractor import BGGClient

client = BGGClient(token="your_token_here")
```

> **Note**: Get your BGG API token from your BoardGameGeek account settings.

## Quick Start

### Python Library
```python
from bgg_extractor import search, get_things, save_json

# Search for games
results = search("Catan")
print(f"Found {len(results.items)} results")

# Get detailed information
games = get_things([13, 174430], stats=True)  # Catan and Gloomhaven

# Save to file
save_json(games.items, "games.json")
```

### Command Line
```bash
# Search for games
bgg-extractor search --query "Gloomhaven" --output results.json

# Get game details
bgg-extractor things --ids 174430 --stats --output gloomhaven.json

# Get user collection
bgg-extractor collection --username eekspider --stats --output collection.csv
```

## CLI Usage

### Available Commands

#### search
Search for board games by name.

```bash
bgg-extractor search --query "Wingspan" --output results.json
bgg-extractor search --query "Pandemic" --type boardgame --exact
```

**Options:**
- `--query, -q`: Search query (required)
- `--type, -t`: Filter by type (boardgame, rpg, etc.)
- `--exact`: Exact match only
- `--output, -o`: Output file path
- `--format, -f`: Output format (json or csv)

#### things
Get detailed information about specific games.

```bash
bgg-extractor things --ids 174430 13 --stats --output games.json
```

**Options:**
- `--ids`: Game IDs (required, space-separated)
- `--type`: Filter by type
- `--stats`: Include statistics
- `--videos`: Include videos
- `--versions`: Include version information
- `--output, -o`: Output file path
- `--format, -f`: Output format (json or csv)

#### collection
Get a user's game collection.

```bash
bgg-extractor collection --username eekspider --stats --output collection.csv
```

**Options:**
- `--username, -u`: BGG username (required)
- `--stats`: Include statistics
- `--brief`: Return abbreviated results
- `--subtype`: Item subtype filter
- `--output, -o`: Output file path
- `--format, -f`: Output format (json or csv)

#### plays
Get a user's play history.

```bash
bgg-extractor plays --username eekspider --output plays.json
```

**Options:**
- `--username, -u`: BGG username (required)
- `--id`: Filter by specific game ID
- `--mindate`: Minimum date (YYYY-MM-DD)
- `--maxdate`: Maximum date (YYYY-MM-DD)
- `--output, -o`: Output file path
- `--format, -f`: Output format (json or csv)

## Python Library Usage

### Synchronous API (Recommended for Scripts)

Simple, blocking functions perfect for scripts and notebooks:

```python
from bgg_extractor import (
    search,
    get_things,
    get_collection,
    get_plays,
    get_user,
    save_json,
    save_csv
)

# All functions handle async internally
results = search("Wingspan")
games = get_things([266192], stats=True)
collection = get_collection("eekspider", stats=True)
```

### Async API (For Advanced Use)

For maximum performance in async applications:

```python
import asyncio
from bgg_extractor import BGGClient

async def fetch_data():
    async with BGGClient(token="your_token") as client:
        # Search
        results = await client.search("Gloomhaven")

        # Get games
        games = await client.get_thing([174430], stats=True)

        # Get collection
        collection = await client.get_collection("username", stats=True)

        return games

# Run async function
games = asyncio.run(fetch_data())
```

### Working with Data

#### Accessing Game Information
```python
games = get_things([13], stats=True)

for game in games.items:
    print(f"Name: {game.name}")
    print(f"Year: {game.yearpublished}")
    print(f"Players: {game.minplayers}-{game.maxplayers}")
    print(f"Description: {game.description[:100]}...")
```

#### Batch Processing with Rate Limits

The BGG API has a 20-item limit per request:

```python
from bgg_extractor import BGGClient
import asyncio

async def fetch_many_games(game_ids):
    batch_size = 20
    all_games = []

    async with BGGClient() as client:
        for i in range(0, len(game_ids), batch_size):
            batch = game_ids[i:i+batch_size]
            print(f"Fetching batch {i//batch_size + 1}...")
            result = await client.get_thing(batch, stats=True)
            all_games.extend(result.items)

    return all_games

game_ids = list(range(1, 101))
games = asyncio.run(fetch_many_games(game_ids))
```

#### Saving Data
```python
from bgg_extractor import save_json, save_csv

# Save as JSON
save_json(games.items, "games.json")

# Save as CSV
save_csv(games.items, "games.csv")
```

#### Data Transformation
```python
from bgg_extractor.transform import models_to_list, model_to_dict
import pandas as pd

# Convert to list of dictionaries
games_dict = models_to_list(games.items)

# Create DataFrame
df = pd.DataFrame(games_dict)
print(df.head())

# Save DataFrame
df.to_csv("games_processed.csv", index=False)
```

#### Stream to Disk (Memory Efficient)

For large datasets, stream directly to disk:

```python
import json
from bgg_extractor import BGGClient

async def stream_to_disk(game_ids, output_file):
    batch_size = 20

    async with BGGClient() as client:
        with open(output_file, 'w') as f:
            for i in range(0, len(game_ids), batch_size):
                batch = game_ids[i:i+batch_size]
                result = await client.get_thing(batch, stats=True)

                # Write each game as JSON line
                for game in result.items:
                    f.write(json.dumps(game.model_dump()) + '\n')

# Later, read back with pandas
import pandas as pd
df = pd.read_json("games.jsonl", lines=True)
```

## Troubleshooting

### Common Issues

#### "BGG_API_TOKEN is required"
**Solution**: Set the `BGG_API_TOKEN` environment variable or create a `.env` file.

#### "Cannot load more than 20 items"
**Solution**: The BGG API limits requests to 20 items. Use batch processing (see examples above).

#### "This event loop is already running" (Jupyter)
**Solution**: Use the async API directly with `await` in Jupyter notebooks instead of sync wrappers.

```python
# Instead of:
results = search("Catan")  # Won't work in Jupyter

# Use:
async with BGGClient(token=token) as client:
    results = await client.search("Catan")
```

#### Rate Limiting / 429 Errors
**Solution**: The library includes automatic throttling (2-second delay between requests). If you still encounter issues, increase `min_delay`:

```python
from bgg_extractor import BGGClient

async with BGGClient(min_delay=5.0) as client:  # 5-second delay
    results = await client.search("Catan")
```

#### 202 Queued Responses
The BGG API sometimes queues requests. The library automatically retries up to 12 times with exponential backoff. If needed, adjust:

```python
async with BGGClient(max_poll_attempts=20) as client:
    results = await client.search("Catan")
```

### Getting Help

- **Documentation**: Check the [API Reference](api_reference.md)
- **Examples**: See [Usage Examples](examples.md)
- **Issues**: Report bugs on GitHub
- **BGG API Docs**: [BGG XML API2 Documentation](https://boardgamegeek.com/wiki/page/BGG_XML_API2)
