import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from bgg_extractor.storage.local import LocalStorage


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture to provide a temporary directory for storage tests."""
    d = tmp_path / "storage_test"
    d.mkdir()
    yield d
    shutil.rmtree(d)


def test_write_bytes(temp_dir):
    storage = LocalStorage(base_path=str(temp_dir))
    data = b"hello world"
    path = "test.txt"

    out_path = storage.write_bytes(path, data)

    assert Path(out_path).exists()
    assert Path(out_path).read_bytes() == data
    assert str(temp_dir) in out_path


def test_write_json(temp_dir):
    storage = LocalStorage(base_path=str(temp_dir))
    data = {"key": "value", "list": [1, 2, 3]}
    path = "test.json"

    out_path = storage.write_json(path, data)

    assert Path(out_path).exists()
    with open(out_path) as f:
        loaded = json.load(f)
    assert loaded == data


def test_write_dataframe_parquet(temp_dir):
    storage = LocalStorage(base_path=str(temp_dir))
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = "test.parquet"

    out_path = storage.write_dataframe(path, df, fmt="parquet")

    assert Path(out_path).exists()
    loaded = pd.read_parquet(out_path)
    pd.testing.assert_frame_equal(df, loaded)


def test_write_dataframe_csv(temp_dir):
    storage = LocalStorage(base_path=str(temp_dir))
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = "test.csv"

    out_path = storage.write_dataframe(path, df, fmt="csv")

    assert Path(out_path).exists()
    loaded = pd.read_csv(out_path)
    pd.testing.assert_frame_equal(df, loaded)


def test_write_dataframe_json(temp_dir):
    storage = LocalStorage(base_path=str(temp_dir))
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = "test.json"

    out_path = storage.write_dataframe(path, df, fmt="json")

    assert Path(out_path).exists()
    with open(out_path) as f:
        loaded = json.load(f)
    # DataFrame to dict list
    expected = df.to_dict(orient="records")
    assert loaded == expected


def test_write_dataframe_ndjson(temp_dir):
    storage = LocalStorage(base_path=str(temp_dir))
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = "test.ndjson"

    out_path = storage.write_dataframe(path, df, fmt="json", ndjson=True)

    assert Path(out_path).exists()
    with open(out_path) as f:
        lines = f.readlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"a": 1, "b": "x"}
