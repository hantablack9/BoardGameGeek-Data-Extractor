"""Transformation utilities for BGG Extractor data.

This module provides helper functions to convert Pydantic models returned by the client
into standard Python dictionaries or lists of dictionaries, suitable for further processing
or analysis (e.g., with Pandas).
"""

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel


def model_to_dict(model: BaseModel) -> dict[str, Any]:
    """Convert a single Pydantic model to a dictionary.

    Args:
        model: The Pydantic model instance.

    Returns:
        A dictionary representation of the model.
    """
    return model.model_dump()


def models_to_list(models: Sequence[BaseModel]) -> list[dict[str, Any]]:
    """Convert a sequence of Pydantic models to a list of dictionaries.

    Args:
        models: A sequence (list, tuple) of Pydantic model instances.

    Returns:
        A list of dictionaries.
    """
    return [m.model_dump() for m in models]
