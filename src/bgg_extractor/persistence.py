"""Persistence utilities for BGG Extractor data.

This module provides high-level functions to save extracted data to files
in various formats (JSON, CSV).
"""

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from bgg_extractor.writer import save_to_csv as _save_to_csv
from bgg_extractor.writer import save_to_json as _save_to_json


def save_json(data: BaseModel | Sequence[BaseModel] | dict | list, filename: str | Path) -> None:
    """Save data to a JSON file.

    Args:
        data: A Pydantic model, a list of models, or a dict/list.
        filename: The output filename.
    """
    _save_to_json(data, filename)


def save_csv(data: Sequence[BaseModel] | Sequence[dict], filename: str | Path) -> None:
    """Save a list of data items to a CSV file.

    Args:
        data: A list of Pydantic models or dictionaries.
        filename: The output filename.
    """
    _save_to_csv(data, filename)
