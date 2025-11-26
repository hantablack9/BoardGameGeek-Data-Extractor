"""Tests for persistence module."""

import tempfile
from pathlib import Path

from bgg_extractor.persistence import save_csv, save_json
from bgg_extractor.schemas import ThingItem


def test_save_json():
    """Test saving data to JSON."""
    items = [
        ThingItem(id=1, name="Game1", type="boardgame"),
        ThingItem(id=2, name="Game2", type="boardgame"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.json"
        save_json(items, output_path)

        assert output_path.exists()
        # Verify content
        import json

        with open(output_path) as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["id"] == 1


def test_save_csv():
    """Test saving data to CSV."""
    items = [
        ThingItem(id=1, name="Game1", type="boardgame"),
        ThingItem(id=2, name="Game2", type="boardgame"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.csv"
        save_csv(items, output_path)

        assert output_path.exists()
        # Verify content
        import csv

        with open(output_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["id"] == "1"
