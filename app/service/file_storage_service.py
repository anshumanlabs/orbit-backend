import os
import boto3
from typing import Any
from uuid import uuid4


def upload_bytes_to_s3(
    file_bytes: bytes,
    *,
    filename: str,
    content_type: str | None = None,
    bucket_name: str | None = None,
    prefix: str | None = None,
    client: Any | None = None,
) -> dict[str, Any]:
    if not file_bytes:
        raise ValueError("No file content provided")

    resolved_bucket = bucket_name or os.getenv("S3_BUCKET_NAME")
    if not resolved_bucket:
        raise ValueError("S3_BUCKET_NAME is not configured")

    if client is None:

        client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )

    safe_name = os.path.basename(filename or "upload.bin")
    key_prefix = (prefix or "uploads").strip("/")
    key = f"{key_prefix}/{uuid4().hex}-{safe_name}" if key_prefix else f"{uuid4().hex}-{safe_name}"

    client.put_object(
        Bucket=resolved_bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type or "application/octet-stream",
    )

    return {
        "bucket": resolved_bucket,
        "key": key,
        "filename": safe_name,
        "content_type": content_type or "application/octet-stream",
    }
