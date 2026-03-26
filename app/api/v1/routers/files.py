import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AttachedFile, Transaction, User
from app.schemas.transactions import AttachedFileOut
from app.service.auth.dependencies import get_current_user
from app.core.settings import settings

router = APIRouter(prefix="/files", tags=["files"])

# ---------------------------------------------------------------------------
# S3 client (works with AWS S3, MinIO, Yandex Object Storage, etc.)
# ---------------------------------------------------------------------------
s3 = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,  # None for real AWS
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name=settings.S3_REGION,
)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def _s3_key(user_id: int, filename: str) -> str:
    return f"users/{user_id}/{uuid.uuid4()}_{filename}"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/upload",
    response_model=AttachedFileOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a file and attach it to a transaction."""

    # Check transaction ownership
    tx = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{file.content_type}' is not allowed. "
            f"Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB",
        )

    # Upload to S3
    key = _s3_key(current_user.id, file.filename)
    try:
        s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Storage error: {e.response['Error']['Message']}",
        )

    # Persist metadata
    attached = AttachedFile(
        transaction_id=transaction_id,
        user_id=current_user.id,
        original_name=file.filename,
        s3_key=key,
        content_type=file.content_type,
        size_bytes=len(contents),
    )
    db.add(attached)
    db.commit()
    db.refresh(attached)
    return attached


@router.get("/transaction/{transaction_id}", response_model=list[AttachedFileOut])
def list_files(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all files attached to a transaction."""
    tx = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return (
        db.query(AttachedFile)
        .filter(
            AttachedFile.transaction_id == transaction_id,
            AttachedFile.user_id == current_user.id,
        )
        .all()
    )


@router.get("/{file_id}/download-url")
def get_download_url(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a temporary pre-signed URL for downloading a file (expires in 15 min)."""
    file = (
        db.query(AttachedFile)
        .filter(
            AttachedFile.id == file_id,
            AttachedFile.user_id == current_user.id,
        )
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": file.s3_key},
            ExpiresIn=900,  # 15 minutes
        )
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not generate URL: {e.response['Error']['Message']}",
        )

    return {
        "url": url,
        "filename": file.original_name,
        "content_type": file.content_type,
        "expires_in": 900,
    }


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a file from S3 and remove its metadata."""
    file = (
        db.query(AttachedFile)
        .filter(
            AttachedFile.id == file_id,
            AttachedFile.user_id == current_user.id,
        )
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Remove from S3 (soft-fail: log but don't block DB cleanup)
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=file.s3_key)
    except ClientError:
        pass  # log in production

    db.delete(file)
    db.commit()
