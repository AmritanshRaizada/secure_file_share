from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from datetime import timedelta
import os
import magic
from typing import List

from app.models.file import File as FileModel
from app.schemas.file import FileInDB, FileDownloadLink
from app.utils.auth import get_current_active_user, get_current_ops_user
from app.utils.security import generate_access_token, is_valid_file_type
from app.config import settings

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "uploads"
ALLOWED_FILE_TYPES = [".pptx", ".docx", ".xlsx"]

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", response_model=FileInDB)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_ops_user),
    db=Depends(get_db)
):
    # Check file type
    if not is_valid_file_type(file.filename, ALLOWED_FILE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {', '.join(ALLOWED_FILE_TYPES)} files are allowed",
        )
    
    # Verify file content type using python-magic
    file_content = await file.read()
    mime = magic.Magic()
    detected_type = mime.from_buffer(file_content)
    
    valid_mime_types = [
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",    # docx
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",         # xlsx
    ]
    
    if detected_type not in valid_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file content type",
        )
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{secrets.token_hex(8)}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create file record in DB
    file_data = {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(file_content),
        "file_path": file_path,
        "uploaded_by": str(current_user["_id"]),
    }
    
    file_record = await FileModel(db).create_file(file_data)
    return file_record

@router.get("/download/{file_id}", response_model=FileDownloadLink)
async def generate_download_link(
    file_id: str,
    current_user: dict = Depends(get_current_active_user),
    db=Depends(get_db)
):
    file = await FileModel(db).get_file_by_id(file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    # Generate secure access token
    access_token = generate_access_token()
    await FileModel(db).update_file(file_id, {"access_token": access_token})
    
    download_link = f"{settings.base_url}/files/download?token={access_token}"
    return {"download_link": download_link, "message": "success"}

@router.get("/download")
async def download_file(
    token: str,
    current_user: dict = Depends(get_current_active_user),
    db=Depends(get_db)
):
    file = await FileModel(db).get_file_by_access_token(token)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied",
        )
    
    # Verify the file exists on disk
    if not os.path.exists(file["file_path"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server",
        )
    
    return FileResponse(
        file["file_path"],
        filename=file["filename"],
        media_type=file["content_type"],
    )

@router.get("/list", response_model=List[FileInDB])
async def list_files(
    current_user: dict = Depends(get_current_active_user),
    db=Depends(get_db)
):
    files = await FileModel(db).get_files_by_uploader(str(current_user["_id"]))
    return files

async def get_db():
    from app.config import settings
    import motor.motor_asyncio
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    try:
        yield db
    finally:
        client.close()