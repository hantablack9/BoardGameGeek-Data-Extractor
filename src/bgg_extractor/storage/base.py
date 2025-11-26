"""
Storage backend interface for BGG Extractor.
"""

from abc import ABC, abstractmethod
from typing import Any


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def write_bytes(self, path: str, data: bytes) -> str:
        """Write raw bytes to a file.

        Args:
            path: Relative path to the file.
            data: Bytes to write.

        Returns:
            The URI or path of the written file.
        """
        raise NotImplementedError

    @abstractmethod
    def write_json(self, path: str, obj: Any) -> str:
        """Write a Python object as JSON.

        Args:
            path: Relative path to the file.
            obj: The object to serialize.

        Returns:
            The URI or path of the written file.
        """
        raise NotImplementedError

    @abstractmethod
    def write_dataframe(self, path: str, df, fmt: str = "parquet", **kwargs) -> str:
        """Write a pandas DataFrame to a file.

        Args:
            path: Relative path to the file.
            df: The pandas DataFrame.
            fmt: Output format ('parquet', 'csv', 'json').
            **kwargs: Additional arguments for the writer.

        Returns:
            The URI or path of the written file.
        """
        raise NotImplementedError
