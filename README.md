# BoardGameGeek Data Extractor

[![Release](https://img.shields.io/github/v/release/hantablack9/BoardGameGeek-Data-Extractor)](https://img.shields.io/github/v/release/hantablack9/BoardGameGeek-Data-Extractor)
[![Build status](https://img.shields.io/github/actions/workflow/status/hantablack9/BoardGameGeek-Data-Extractor/main.yml?branch=main)](https://github.com/hantablack9/BoardGameGeek-Data-Extractor/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/hantablack9/BoardGameGeek-Data-Extractor/branch/main/graph/badge.svg)](https://codecov.io/gh/hantablack9/BoardGameGeek-Data-Extractor)
[![Commit activity](https://img.shields.io/github/commit-activity/m/hantablack9/BoardGameGeek-Data-Extractor)](https://img.shields.io/github/commit-activity/m/hantablack9/BoardGameGeek-Data-Extractor)
[![License](https://img.shields.io/github/license/hantablack9/BoardGameGeek-Data-Extractor)](https://img.shields.io/github/license/hantablack9/BoardGameGeek-Data-Extractor)

A production-grade Python library for extracting, transforming, and persisting data from the BoardGameGeek XML API2.

## Features

- 🎯 **Simple Synchronous API** - Easy-to-use functions for scripts and notebooks
- ⚡ **Async Support** - High-performance async client for advanced use cases
- 📊 **Data Persistence** - Save to JSON and CSV formats
- 🔄 **Data Transformation** - Convert Pydantic models to dicts and DataFrames
- 🎮 **Comprehensive Coverage** - Search, games, collections, plays, users, and families
- 🛡️ **Robust** - Built-in rate limiting, retry logic, and error handling
- 🔑 **Secure** - API token authentication
- 📝 **Well-Documented** - Extensive guides, API reference, and examples

## Documentation

📚 **[User Guide](docs/user_guide.md)** - Installation, configuration, and usage

📖 **[API Reference](docs/api_reference.md)** - Complete API documentation

💡 **[Examples](docs/examples.md)** - Real-world usage examples

## Quick Start

### Installation

```bash
pip install -e .
# or with uv
uv add .
```

### Configuration

Set your BGG API token (required):

```bash
# Create a .env file
echo "BGG_API_TOKEN=your_token_here" > .env
```

### CLI Usage

```bash
# Search for a game
bgg-extractor search --query "Wingspan" --output results.json

# Get game details
bgg-extractor things --ids 174430 13 --stats --output games.json

# Get user collection
bgg-extractor collection --username eekspider --stats --output collection.csv
```

### Python Library

```python
from bgg_extractor import search, get_things, save_json

# Search for a game
results = search("Catan")
print(f"Found {len(results.items)} items")

# Get game details
game_ids = [item.id for item in results.items[:5]]
games = get_things(game_ids, stats=True)

# Save to file
save_json(games.items, "catan_games.json")
```

## Development

- Run tests: `pytest`
- Lint: `ruff check src`
- Typecheck: `mypy src`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
