import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import Transaction
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db import User
from app.db.database import get_db
from app.db.models import AttachedFile
from app.schemas.files import AttachedFileOut
from app.service.auth.dependencies import get_current_user

router = APIRouter(prefix="/files", tags=["files"])

# ─── S3 клиент (boto3 работает с MinIO через endpoint_url) ────────────────────
s3 = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,  # "http://minio:9000" для MinIO
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name=settings.S3_REGION,
)

# ─── Ограничения ─────────────────────────────────────────────────────────────
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
    """Генерирует уникальный ключ объекта в S3."""
    return f"users/{user_id}/{uuid.uuid4()}_{filename}"


# ─── POST /files/upload ───────────────────────────────────────────────────────
@router.post(
    "/upload",
    response_model=AttachedFileOut,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить файл и привязать к транзакции",
)
async def upload_file(
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Проверка владения транзакцией
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

    # 2. Валидация типа файла
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Тип файла '{file.content_type}' не разрешён. "
                f"Допустимые: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            ),
        )

    # 3. Читаем и проверяем размер
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл слишком большой. Максимум: {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB",
        )

    # 4. Загружаем в S3/MinIO
    key = _s3_key(current_user.id, file.filename)
    try:
        s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка хранилища: {exc.response['Error']['Message']}",
        )

    # 5. Сохраняем метаданные в БД
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


# ─── GET /files/transaction/{id} ─────────────────────────────────────────────
@router.get(
    "/transaction/{transaction_id}",
    response_model=list[AttachedFileOut],
    summary="Список файлов транзакции",
)
def list_files(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем право доступа
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


# ─── GET /files/{id}/download-url ────────────────────────────────────────────
@router.get(
    "/{file_id}/download-url",
    summary="Pre-signed URL для скачивания (15 мин)",
)
def get_download_url(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file = _get_own_file(db, file_id, current_user.id)

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": file.s3_key},
            ExpiresIn=900,  # 15 минут
        )
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Не удалось создать ссылку: {exc.response['Error']['Message']}",
        )

    return {
        "url": url,
        "filename": file.original_name,
        "content_type": file.content_type,
        "expires_in": 900,
    }


# ─── DELETE /files/{id} ──────────────────────────────────────────────────────
@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить файл из S3 и очистить метаданные",
)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file = _get_own_file(db, file_id, current_user.id)

    # Удаляем из S3 (не блокируем если S3 недоступен)
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=file.s3_key)
    except ClientError:
        pass  # в production — логировать

    # Удаляем метаданные из БД
    db.delete(file)
    db.commit()


# ─── helper ──────────────────────────────────────────────────────────────────
def _get_own_file(db: Session, file_id: int, user_id: int) -> AttachedFile:
    f = (
        db.query(AttachedFile)
        .filter(
            AttachedFile.id == file_id,
            AttachedFile.user_id == user_id,
        )
        .first()
    )
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    return f
