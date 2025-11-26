# BGG Extractor Usage Examples

Real-world usage examples for common tasks with the BGG Extractor library.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Data Collection Workflows](#data-collection-workflows)
- [Data Processing](#data-processing)
- [Integration Examples](#integration-examples)
- [Advanced Patterns](#advanced-patterns)

## Basic Examples

### Search and Explore

```python
from bgg_extractor import search, get_things

# Search for a game
results = search("Wingspan")
print(f"Found {len(results.items)} results")

# Get the first result's ID
if results.items:
    game_id = results.items[0].id

    # Get detailed information
    game = get_things([game_id], stats=True)
    print(f"Name: {game.items[0].name}")
    print(f"Rating: {game.items[0].average}")
    print(f"Rank: {game.items[0].rank}")
```

### Get Top Rated Games

```python
from bgg_extractor import get_things

# Get details for top games (by ID)
top_game_ids = [174430, 161936, 167791, 182028, 266192]  # Gloomhaven, Pandemic Legacy, etc.
games = get_things(top_game_ids, stats=True)

for game in games.items:
    print(f"{game.name} - Rank: {game.rank}, Rating: {game.average}")
```

### Analyze User Collection

```python
from bgg_extractor import get_collection

username = "eekspider"
collection = get_collection(username, stats=True)

print(f"{username} owns {len(collection.items)} games")

# Find most played games
plays = [(item.name, item.numplays) for item in collection.items if item.numplays > 0]
plays.sort(key=lambda x: x[1], reverse=True)

print("\nTop 5 most played:")
for name, count in plays[:5]:
    print(f"  {name}: {count} plays")
```

## Data Collection Workflows

### Build a Game Database

```python
import asyncio
from bgg_extractor import BGGClient, save_json
import json

async def build_game_database(game_ids, output_file):
    """Fetch game data in batches and save to disk."""
    batch_size = 20

    async with BGGClient() as client:
        with open(output_file, 'w') as f:
            for i in range(0, len(game_ids), batch_size):
                batch = game_ids[i:i+batch_size]
                print(f"Fetching batch {i//batch_size + 1}/{(len(game_ids)-1)//batch_size + 1}...")

                result = await client.get_thing(batch, stats=True)

                # Write each game as a JSON line
                for game in result.items:
                    f.write(json.dumps(game.model_dump()) + '\n')

    print(f"Saved {len(game_ids)} games to {output_file}")

# Fetch top 1000 games
game_ids = list(range(1, 1001))
asyncio.run(build_game_database(game_ids, "games_database.jsonl"))
```

### Track User Activity Over Time

```python
from bgg_extractor import get_plays
from datetime import datetime, timedelta

username = "eekspider"

# Get plays from last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

plays = get_plays(
    username=username,
    mindate=start_date.strftime("%Y-%m-%d"),
    maxdate=end_date.strftime("%Y-%m-%d")
)

print(f"{username} logged {len(plays.plays)} plays in the last 30 days")

# Count plays by game
from collections import Counter
game_plays = Counter(play.item['name'] for play in plays.plays)

print("\nMost played games:")
for game, count in game_plays.most_common(5):
    print(f"  {game}: {count} plays")
```

### Extract Games by Category

```python
from bgg_extractor import search, get_things

# Search for strategy games
results = search("strategy", type="boardgame")

# Get detailed info
game_ids = [item.id for item in results.items[:20]]
games = get_things(game_ids, stats=True)

# Filter by category
strategy_games = [
    game for game in games.items
    if any("Strategy" in cat for cat in game.categories)
]

print(f"Found {len(strategy_games)} strategy games")
```

## Data Processing

### Create a Pandas DataFrame

```python
from bgg_extractor import get_things
from bgg_extractor.transform import models_to_list
import pandas as pd

# Fetch games
games = get_things([13, 174430, 266192, 161936], stats=True)

# Convert to DataFrame
games_dict = models_to_list(games.items)
df = pd.DataFrame(games_dict)

# Select columns
df = df[['id', 'name', 'yearpublished', 'minplayers', 'maxplayers', 'average', 'rank']]

print(df.to_string())
```

### Analyze Game Complexity

```python
import pandas as pd
from bgg_extractor import get_things
from bgg_extractor.transform import models_to_list

# Get a range of games
game_ids = list(range(1, 101))
games = get_things(game_ids, stats=True)

# Convert to DataFrame
df = pd.DataFrame(models_to_list(games.items))

# Analyze complexity by play time
df_clean = df[df['playingtime'].notna() & df['average'].notna()]

print("Average rating by play time:")
print(df_clean.groupby(pd.cut(df_clean['playingtime'], bins=[0, 30, 60, 120, 300]))['average'].mean())
```

### Extract Text for RAG/LLM Applications

```python
from bgg_extractor import get_things

# Get games with descriptions
game_ids = [174430, 266192, 161936]  # Gloomhaven, Wingspan, Pandemic Legacy
games = get_things(game_ids, stats=True)

# Extract and format descriptions
for game in games.items:
    if game.description:
        print(f"\n{'='*60}")
        print(f"Game: {game.name} ({game.yearpublished})")
        print(f"{'='*60}")
        print(f"\nDescription:\n{game.description}")
        print(f"\nCategories: {', '.join(game.categories)}")
        print(f"Mechanics: {', '.join(game.mechanics)}")
```

## Integration Examples

### Build a Recommendation Dataset

```python
import pandas as pd
from bgg_extractor import get_things, get_collection
from bgg_extractor.transform import models_to_list

def build_recommendation_dataset(usernames):
    """Build a user-game matrix for recommendations."""
    all_games = set()
    user_ratings = {}

    for username in usernames:
        print(f"Fetching collection for {username}...")
        collection = get_collection(username, stats=True)

        user_ratings[username] = {}
        for item in collection.items:
            if item.status and item.status.get('own') == 1:
                all_games.add(item.objectid)
                # Use user rating if available, otherwise use BGG average
                rating = item.stats.get('rating', {}).get('value') if item.stats else None
                user_ratings[username][item.objectid] = rating

    # Create DataFrame
    df = pd.DataFrame(user_ratings).fillna(0)
    return df

# Example usage
usernames = ["eekspider", "username2", "username3"]
ratings_matrix = build_recommendation_dataset(usernames)
print(ratings_matrix.head())
```

### Export for Tableau/PowerBI

```python
from bgg_extractor import get_things
from bgg_extractor.transform import models_to_list
import pandas as pd

# Fetch comprehensive game data
game_ids = list(range(1, 201))
games = get_things(game_ids, stats=True)

# Convert to DataFrame
df = pd.DataFrame(models_to_list(games.items))

# Clean and prepare for BI tools
df['category_count'] = df['categories'].apply(len)
df['mechanic_count'] = df['mechanics'].apply(len)
df['designer_count'] = df['designers'].apply(len)

# Export
df.to_csv("games_for_tableau.csv", index=False)
df.to_excel("games_for_powerbi.xlsx", index=False)
print("Exported data for Tableau and PowerBI")
```

### Create a Game Catalog Website

```python
from bgg_extractor import search, get_things
from bgg_extractor.transform import models_to_list
import json

def create_game_catalog(search_terms):
    """Create a JSON catalog for a web application."""
    catalog = []

    for term in search_terms:
        print(f"Searching for: {term}")
        results = search(term)

        # Get top 5 results
        game_ids = [item.id for item in results.items[:5]]
        games = get_things(game_ids, stats=True)

        catalog.extend(models_to_list(games.items))

    # Export as JSON for web app
    with open("game_catalog.json", 'w') as f:
        json.dump(catalog, f, indent=2)

    return catalog

search_terms = ["strategy", "family", "party", "cooperative"]
catalog = create_game_catalog(search_terms)
print(f"Created catalog with {len(catalog)} games")
```

## Advanced Patterns

### Concurrent Fetching with Rate Limiting

```python
import asyncio
from bgg_extractor import BGGClient

async def fetch_with_semaphore(client, game_ids, max_concurrent=3):
    """Fetch games with controlled concurrency."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_batch(batch):
        async with semaphore:
            return await client.get_thing(batch, stats=True)

    # Split into batches of 20
    batches = [game_ids[i:i+20] for i in range(0, len(game_ids), 20)]

    # Fetch concurrently with semaphore
    tasks = [fetch_batch(batch) for batch in batches]
    results = await asyncio.gather(*tasks)

    # Combine results
    all_games = []
    for result in results:
        all_games.extend(result.items)

    return all_games

async def main():
    game_ids = list(range(1, 101))

    async with BGGClient() as client:
        games = await fetch_with_semaphore(client, game_ids, max_concurrent=3)
        print(f"Fetched {len(games)} games")

asyncio.run(main())
```

### Incremental Data Updates

```python
import json
from pathlib import Path
from datetime import datetime
from bgg_extractor import get_collection

def update_collection_tracking(username, data_dir="data"):
    """Track collection changes over time."""
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)

    # Fetch current collection
    collection = get_collection(username, stats=True)

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = data_path / f"{username}_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump([item.model_dump() for item in collection.items], f, indent=2)

    print(f"Saved collection snapshot: {filename}")
    return filename

# Run daily/weekly to track changes
update_collection_tracking("eekspider")
```

### Error Handling and Retry Logic

```python
import asyncio
from bgg_extractor import BGGClient

async def fetch_with_retry(client, game_ids, max_retries=3):
    """Fetch with custom retry logic."""
    for attempt in range(max_retries):
        try:
            result = await client.get_thing(game_ids, stats=True)
            return result
        except RuntimeError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts")
                raise

async def main():
    async with BGGClient() as client:
        try:
            games = await fetch_with_retry(client, [13, 174430])
            print(f"Successfully fetched {len(games.items)} games")
        except RuntimeError as e:
            print(f"Error: {e}")

asyncio.run(main())
```

### Memory-Efficient Large-Scale Processing

```python
import asyncio
from bgg_extractor import BGGClient
import json

async def process_large_dataset(game_ids, output_file, batch_size=20):
    """Process large datasets without loading all into memory."""
    total_batches = (len(game_ids) - 1) // batch_size + 1

    async with BGGClient() as client:
        with open(output_file, 'w') as f:
            for i in range(0, len(game_ids), batch_size):
                batch = game_ids[i:i+batch_size]
                batch_num = i // batch_size + 1

                print(f"Processing batch {batch_num}/{total_batches}...")

                try:
                    result = await client.get_thing(batch, stats=True)

                    # Stream to disk immediately
                    for game in result.items:
                        f.write(json.dumps(game.model_dump()) + '\n')

                except Exception as e:
                    print(f"Error in batch {batch_num}: {e}")
                    continue

    print(f"Completed processing {len(game_ids)} games")

# Process 10,000 games
game_ids = list(range(1, 10001))
asyncio.run(process_large_dataset(game_ids, "large_dataset.jsonl"))
```

These examples demonstrate the flexibility and power of the BGG Extractor library for various data collection and analysis tasks!
