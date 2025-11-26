"""
S3 storage backend setup.
"""

import boto3

from bgg_extractor.storage.base import StorageBackend


class S3Storage(StorageBackend):
    """S3 storage backend using boto3.

    Writes data to an S3 bucket.
    """

    def __init__(self, bucket: str, prefix: str | None = None, boto3_session: boto3.session.Session | None = None):
        """Initialize S3Storage.

        Args:
            bucket: Name of the S3 bucket.
            prefix: Optional prefix for all keys.
            boto3_session: Optional boto3 Session to use. If None, creates a default client.
        """
        self.bucket = bucket
        self.prefix = (prefix.rstrip("/") + "/") if prefix else ""
        self.s3 = boto3_session.client("s3") if boto3_session else boto3.client("s3")

    def _key(self, path: str) -> str:
        """Generate the full S3 key for a given path.

        Args:
            path: Relative path.

        Returns:
            Full S3 key string.
        """
        return f"{self.prefix}{path.lstrip('/')}"

    def write_bytes(self, path: str, data: bytes) -> str:
        """Write raw bytes to S3.

        Args:
            path: Relative path (key suffix).
            data: Bytes to write.

        Returns:
            The S3 URI (s3://bucket/key).
        """
        key = self._key(path)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"s3://{self.bucket}/{key}"

    def write_json(self, path: str, obj) -> str:
        """Write a Python object as JSON to S3.

        Args:
            path: Relative path (key suffix).
            obj: The object to serialize.

        Returns:
            The S3 URI.
        """
        import json

        data = json.dumps(obj, default=str, ensure_ascii=False).encode("utf-8")
        return self.write_bytes(path, data)

    def write_dataframe(self, path: str, df, fmt: str = "parquet", **kwargs) -> str:
        """Write a pandas DataFrame to S3.

        Args:
            path: Relative path (key suffix).
            df: The pandas DataFrame.
            fmt: Output format ('parquet', 'csv', 'json').
            **kwargs: Additional arguments for the writer.

        Returns:
            The S3 URI.

        Raises:
            ValueError: If an unsupported format is specified.
        """
        import io

        fmt = fmt.lower()
        buf = io.BytesIO()
        if fmt == "parquet":
            try:
                import pyarrow as pa
                import pyarrow.parquet as pq

                table = pa.Table.from_pandas(df, preserve_index=False)
                pq.write_table(table, buf, **kwargs)
            except Exception:
                df.to_parquet(buf, index=False)
            buf.seek(0)
            return self.write_bytes(path, buf.read())
        elif fmt == "csv":
            buf2 = io.StringIO()
            df.to_csv(buf2, index=False)
            return self.write_bytes(path, buf2.getvalue().encode("utf-8"))
        elif fmt == "json":
            import json

            return self.write_bytes(path, json.dumps(df.to_dict(orient="records"), default=str).encode("utf-8"))
        else:
            raise ValueError("Unsupported format for S3Storage")
