from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileBase(BaseModel):
    filename: str
    content_type: str
    file_size: int

class FileCreate(FileBase):
    pass

class FileInDB(FileBase):
    id: str
    uploaded_by: str
    file_path: str
    access_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FileDownloadLink(BaseModel):
    download_link: str
    message: str = "success"