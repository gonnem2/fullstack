import datetime

from pydantic import BaseModel


class AttachedFileOut(BaseModel):
    id: int
    transaction_id: int
    original_name: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime.datetime

    model_config = {"from_attributes": True}

