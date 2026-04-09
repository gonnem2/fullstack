import pytest
from unittest.mock import AsyncMock, patch
from app.core.s3.service import upload_file


@pytest.mark.asyncio
async def test_upload_file():
    mock_file = AsyncMock()
    mock_file.read = AsyncMock(return_value=b"data")
    mock_file.filename = "test.jpg"
    mock_file.content_type = "image/jpeg"  # обязательно!

    with patch("app.core.s3.service.s3") as mock_s3:
        mock_s3.upload_fileobj = AsyncMock()
        key = await upload_file(mock_file, 1)
        assert key.startswith("users/1/")
