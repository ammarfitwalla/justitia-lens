import os
import aiofiles
from fastapi import UploadFile
from app.config import settings
import uuid

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

async def save_upload_file(file: UploadFile, subfolder: str = "") -> str:
    """
    Saves a specific upload file to the local storage.
    Returns: The absolute file path.
    """
    # Create subfolder if needed (e.g., 'evidence' or 'reports')
    target_dir = os.path.join(settings.STORAGE_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate unique filename to prevent collisions
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(target_dir, unique_filename)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    return file_path
