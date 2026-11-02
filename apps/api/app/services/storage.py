"""Neon Object Storage client.

Uses boto3 against Neon's S3-compatible endpoint. Credentials and endpoint
come from the standard AWS_* env vars pulled by `neon link` or `neon deploy`.
Neon requires path-style addressing.
"""
from uuid import uuid4

import boto3
from botocore.config import Config

from app.config import settings


_s3 = None


def _client():
    global _s3
    if _s3 is None:
        kwargs = {
            "config": Config(
                signature_version="s3v4",  # Neon requires SigV4
                s3={"addressing_style": "path"},
            )
        }
        if settings.aws_endpoint_url_s3:
            kwargs["endpoint_url"] = settings.aws_endpoint_url_s3
        if settings.aws_region:
            kwargs["region_name"] = settings.aws_region
        if settings.aws_access_key_id:
            kwargs["aws_access_key_id"] = settings.aws_access_key_id
            kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        _s3 = boto3.client("s3", **kwargs)
    return _s3


def upload_pdf(data: bytes, filename: str) -> str:
    """Upload PDF bytes to the uploads bucket, return the object key."""
    key = f"docs/{uuid4()}/{filename}"
    _client().put_object(
        Bucket=settings.uploads_bucket,
        Key=key,
        Body=data,
        ContentType="application/pdf",
    )
    return key


def presigned_download_url(key: str, expires_in: int = 3600) -> str:
    """Create a presigned URL for GET on an object key."""
    return _client().generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.uploads_bucket, "Key": key},
        ExpiresIn=expires_in,
    )
