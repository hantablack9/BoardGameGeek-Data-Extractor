from unittest.mock import MagicMock, patch

import pandas as pd

from bgg_extractor.storage.s3 import S3Storage


def test_s3_write_dataframe_parquet(monkeypatch):
    df = pd.DataFrame([{"id": 1, "name": "a"}])
    mock_client = MagicMock()
    mock_client.put_object.return_value = {}
    with patch("bgg_extractor.storage.s3.boto3.client", return_value=mock_client):
        s3 = S3Storage(bucket="my-bucket", prefix="pfx")
        res = s3.write_dataframe("test/out.parquet", df, fmt="parquet")
        assert res.startswith("s3://my-bucket/pfx/test/out.parquet")
