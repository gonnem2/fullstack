import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from app.core.settings import settings

s3 = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name=settings.S3_REGION,
)

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_SIZE = 5 * 1024 * 1024  # 5MB


def generate_key(user_id: int, filename: str) -> str:
    return f"users/{user_id}/{uuid.uuid4()}_{filename}"


async def upload_file(file, user_id: int) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Invalid file type")

    content = await file.read()

    if len(content) > MAX_SIZE:
        raise HTTPException(413, "File too large")

    key = generate_key(user_id, file.filename)

    try:
        s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=content,
            ContentType=file.content_type,
        )
    except ClientError as e:
        raise HTTPException(502, "S3 error")

    return key


def generate_download_url(key: str) -> str:
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": key},
            ExpiresIn=900,
        )
    except ClientError:
        raise HTTPException(502, "Failed to generate URL")


def delete_file(key: str):
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=key)
    except ClientError:
        pass
