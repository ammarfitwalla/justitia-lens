import os
import aiofiles
from fastapi import UploadFile
from app.config import settings
import uuid

# Ensure base storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

async def save_upload_file(file: UploadFile, case_id: int, subfolder: str = "") -> str:
    """
    Saves a specific upload file to the local storage, organized by case ID.
    Files are stored as: data/cases/{case_id}/{subfolder}/{filename}
    Returns: The absolute file path.
    """
    # Create case-specific directory structure: data/cases/{case_id}/{subfolder}
    target_dir = os.path.join(settings.STORAGE_DIR, "cases", str(case_id), subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate unique filename to prevent collisions
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(target_dir, unique_filename)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    return file_path

