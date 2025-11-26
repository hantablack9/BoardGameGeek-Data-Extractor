"""BGG Extractor Library.

A Python library for extracting, transforming, and persisting data from BoardGameGeek XML API2.
"""

from bgg_extractor.client import (
    BGGClient,
    get_collection,
    get_family,
    get_plays,
    get_things,
    get_user,
    search,
)
from bgg_extractor.persistence import save_csv, save_json
from bgg_extractor.transform import model_to_dict, models_to_list

__all__ = [
    "BGGClient",
    "get_collection",
    "get_family",
    "get_plays",
    "get_things",
    "get_user",
    "model_to_dict",
    "models_to_list",
    "save_csv",
    "save_json",
    "search",
]
