"""Data persistence utilities for BGG Extractor.

Supports saving Pydantic models (or lists of models) to JSON and CSV formats.
"""

import csv
import json
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel


def save_to_json(data: BaseModel | Sequence[BaseModel] | dict | list, filename: str | Path) -> None:
    """Save data to a JSON file.

    Args:
        data: A Pydantic model, a list of models, or a dict/list.
        filename: The output filename.
    """
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    def default_serializer(obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        raise TypeError(f"Type {type(obj)} not serializable")

    with open(path, "w", encoding="utf-8") as f:
        if isinstance(data, BaseModel):
            json.dump(data.model_dump(), f, indent=2, default=default_serializer)
        elif isinstance(data, (list, tuple)) and data and isinstance(data[0], BaseModel):
            json.dump([item.model_dump() for item in data], f, indent=2, default=default_serializer)
        else:
            json.dump(data, f, indent=2, default=default_serializer)


def save_to_csv(data: Sequence[BaseModel] | Sequence[dict], filename: str | Path) -> None:
    """Save a list of data items to a CSV file.

    Flattens nested dictionaries/lists into string representations for CSV compatibility.

    Args:
        data: A list of Pydantic models or dictionaries.
        filename: The output filename.
    """
    if not data:
        return

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert models to dicts if needed
    rows = []
    for item in data:
        if isinstance(item, BaseModel):
            rows.append(item.model_dump())
        else:
            rows.append(item)

    if not rows:
        return

    # Determine headers from the first item
    headers = list(rows[0].keys())

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            # Simple flattening: convert complex types to JSON strings or repr
            clean_row = {}
            for k, v in row.items():
                if isinstance(v, (dict, list, tuple)):
                    clean_row[k] = json.dumps(v)
                else:
                    clean_row[k] = v
            writer.writerow(clean_row)
