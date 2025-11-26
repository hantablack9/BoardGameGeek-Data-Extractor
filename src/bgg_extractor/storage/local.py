"""
Local filesystem storage backend for BGG Extractor.
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from bgg_extractor.storage.base import StorageBackend
from bgg_extractor.storage.utils import (
    coerce_dataframe_types,
    normalize_dataframe_columns,
    write_csv_atomic,
    write_parquet_atomic,
)


class LocalStorage(StorageBackend):
    """Local filesystem storage backend.

    Writes data to the local disk, handling directory creation and atomic writes.
    """

    def __init__(self, base_path: str = "."):
        """Initialize LocalStorage.

        Args:
            base_path: The root directory for storing files. Defaults to current directory.
        """
        self.base = Path(base_path).expanduser().resolve()
        self.base.mkdir(parents=True, exist_ok=True)

    def _resolve(self, path: str) -> Path:
        """Resolve a relative path to an absolute path within the base directory.

        Ensures parent directories exist.

        Args:
            path: Relative path string.

        Returns:
            Resolved Path object.
        """
        p = self.base.joinpath(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def write_bytes(self, path: str, data: bytes) -> str:
        """Write raw bytes to a file atomically.

        Args:
            path: Relative path to the file.
            data: Bytes to write.

        Returns:
            The absolute path of the written file as a string.
        """
        p = self._resolve(path)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(p)
        return str(p)

    def write_json(self, path: str, obj: Any, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Write a Python object as JSON atomically.

        Args:
            path: Relative path to the file.
            obj: The object to serialize.
            ensure_ascii: If True, escape non-ASCII characters.
            indent: Indentation level for pretty-printing.

        Returns:
            The absolute path of the written file as a string.
        """
        p = self._resolve(path)
        tmp = p.with_suffix(p.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=ensure_ascii, indent=indent, default=str)
        tmp.replace(p)
        return str(p)

    def write_dataframe(
        self, path: str, df: pd.DataFrame, fmt: str = "parquet", schema: dict[str, str] | None = None, **kwargs
    ) -> str:
        """Write a pandas DataFrame to a file.

        Supports parquet, csv, and json formats. Handles column normalization and type coercion.

        Args:
            path: Relative path to the output file.
            df: The pandas DataFrame to write.
            fmt: Output format ('parquet', 'csv', 'json').
            schema: Optional dictionary mapping column names to types for coercion.
            **kwargs: Additional arguments passed to the underlying writer function.

        Returns:
            The absolute path of the written file as a string.

        Raises:
            ValueError: If an unsupported format is specified.
        """
        df2 = normalize_dataframe_columns(df)
        if schema:
            df2 = coerce_dataframe_types(df2, schema)
        else:
            df2 = coerce_dataframe_types(df2, None)

        if fmt.lower() == "parquet":
            return write_parquet_atomic(df2, self._resolve(path).as_posix(), **kwargs)
        elif fmt.lower() == "csv":
            return write_csv_atomic(df2, self._resolve(path).as_posix(), index=False, **kwargs)
        elif fmt.lower() == "json":
            if kwargs.get("ndjson", False):
                p = self._resolve(path)
                tmp = p.with_suffix(p.suffix + ".tmp")
                with open(tmp, "w", encoding="utf-8") as f:
                    for row in df2.to_dict(orient="records"):
                        f.write(json.dumps(row, default=str, ensure_ascii=False) + "\n")
                tmp.replace(p)
                return str(p)
            else:
                return self.write_json(path, df2.to_dict(orient="records"))
        else:
            raise ValueError("Unsupported format: choose parquet, csv, json")
