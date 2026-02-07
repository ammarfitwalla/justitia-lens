import os
import aiofiles
import httpx
from fastapi import UploadFile
from app.config import settings
import uuid

# Ensure base storage directory exists (for local storage)
os.makedirs(settings.STORAGE_DIR, exist_ok=True)


async def save_upload_file(file: UploadFile, case_id: int, subfolder: str = "") -> str:
    """
    Saves a file either locally or to Supabase Storage based on STORAGE_BACKEND setting.
    Returns: The file path (local) or public URL (Supabase).
    """
    if settings.STORAGE_BACKEND == "supabase":
        return await upload_to_supabase(file, case_id, subfolder)
    else:
        return await save_locally(file, case_id, subfolder)


async def save_locally(file: UploadFile, case_id: int, subfolder: str = "") -> str:
    """
    Saves a file to the local filesystem.
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


async def upload_to_supabase(file: UploadFile, case_id: int, subfolder: str = "") -> str:
    """
    Uploads a file to Supabase Storage using REST API.
    Files are stored as: {bucket}/cases/{case_id}/{subfolder}/{filename}
    Returns: The public URL of the uploaded file.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY.")
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Build storage path
    storage_path = f"cases/{case_id}/{subfolder}/{unique_filename}"
    
    # Read file content
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    
    # Upload via REST API
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{storage_path}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": content_type,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, content=content, headers=headers)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Supabase upload failed: {response.status_code} - {response.text}")
    
    # Return public URL
    public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{storage_path}"
    return public_url


def is_url(path: str) -> bool:
    """Check if a path is a URL (for determining storage type)."""
    return path.startswith("http://") or path.startswith("https://")


async def read_file_content(path: str) -> bytes:
    """
    Read file content from either local path or URL.
    For AI analysis - needs file bytes regardless of storage backend.
    """
    if is_url(path):
        # Fetch from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(path)
            response.raise_for_status()
            return response.content
    else:
        # Read from local filesystem
        async with aiofiles.open(path, 'rb') as f:
            return await f.read()


async def delete_from_supabase(path: str) -> bool:
    """Delete a file from Supabase Storage using REST API."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return False
    
    # Extract storage path from URL if needed
    if is_url(path):
        # Parse URL to get storage path
        # URL format: https://xxx.supabase.co/storage/v1/object/public/{bucket}/{path}
        parts = path.split(f"/storage/v1/object/public/{settings.SUPABASE_BUCKET}/")
        if len(parts) == 2:
            storage_path = parts[1]
        else:
            return False
    else:
        storage_path = path
    
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{storage_path}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            return response.status_code in [200, 204]
    except Exception:
        return False
