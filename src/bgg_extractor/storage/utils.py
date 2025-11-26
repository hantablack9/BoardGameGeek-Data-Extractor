"""
Helper functions for handing column naming patterns, type coercion,
and atomic writes.
"""

import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def normalize_column_name(col: str) -> str:
    """Normalize a column name to be filesystem-safe and consistent.

    Converts to lowercase, removes accents, replaces non-alphanumeric characters with underscores,
    and collapses multiple underscores.

    Args:
        col: The original column name.

    Returns:
        The normalized column name.
    """
    if col is None:
        return ""
    s = str(col).strip()
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^\w]+", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_").lower()
    if s == "":
        s = "col"
    return s


def normalize_dataframe_columns(df: pd.DataFrame, rename_map: dict[str, str] | None = None) -> pd.DataFrame:
    """Normalize all column names in a DataFrame.

    Args:
        df: The input DataFrame.
        rename_map: Optional dictionary to manually rename specific columns.

    Returns:
        A new DataFrame with normalized column names.
    """
    rename_map = rename_map or {}
    new_cols = {}
    for col in df.columns:
        if col in rename_map:
            new_cols[col] = rename_map[col]
        else:
            new_cols[col] = normalize_column_name(col)
    return df.rename(columns=new_cols)


def coerce_dataframe_types(df: pd.DataFrame, schema: dict[str, Any] | None = None) -> pd.DataFrame:
    """Coerce DataFrame columns to specified types or infer them.

    Args:
        df: The input DataFrame.
        schema: Optional dictionary mapping column names to types.

    Returns:
        A new DataFrame with coerced types.
    """
    if schema:
        for col, dtype in schema.items():
            if col not in df.columns:
                df[col] = pd.NA
            try:
                if isinstance(dtype, str) and dtype.startswith("datetime"):
                    df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
                else:
                    df[col] = df[col].astype(dtype, copy=False)
            except Exception:
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                except Exception:
                    df[col] = df[col].astype(object)
        remaining = [c for c in df.columns if c not in schema]
        df = df[[*schema.keys(), *remaining]]
        return df
    else:
        for col in df.columns:
            if df[col].dtype == object:
                sample = df[col].dropna().astype(str)
                if len(sample) == 0:
                    continue
                try_vals = sample.sample(min(len(sample), 20), random_state=0)
                date_like = 0
                for v in try_vals:
                    try:
                        pd.to_datetime(v)
                        date_like += 1
                    except Exception:  # noqa: S110 - Expected to fail for non-date values
                        pass
                if date_like >= len(try_vals) * 0.8:
                    df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
        return df


def write_parquet_atomic(df: pd.DataFrame, out_path: str, **kwargs) -> str:
    """Write DataFrame to Parquet atomically.

    Args:
        df: DataFrame to write.
        out_path: Destination path.
        **kwargs: Arguments for pyarrow.parquet.write_table.

    Returns:
        The output path as a string.
    """

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, tmp.as_posix(), **kwargs)
    tmp.replace(out)
    return out.as_posix()


def write_csv_atomic(df: pd.DataFrame, out_path: str, index: bool = False, **kwargs) -> str:
    """Write DataFrame to CSV atomically.

    Args:
        df: DataFrame to write.
        out_path: Destination path.
        index: Whether to write the index.
        **kwargs: Arguments for df.to_csv.

    Returns:
        The output path as a string.
    """
    import csv

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    csv_kwargs = {
        "index": index,
        "encoding": "utf-8",
        "lineterminator": "\n",
        "quoting": csv.QUOTE_MINIMAL,
    }
    csv_kwargs.update(kwargs)
    df.to_csv(tmp.as_posix(), **csv_kwargs)
    tmp.replace(out)
    return out.as_posix()
