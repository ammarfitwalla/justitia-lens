import google.generativeai as genai
from app.config import settings
from app.services.base_provider import BaseAIProvider
from typing import Optional
import json
import asyncio
import time
import threading
import mimetypes
from google.api_core.exceptions import ResourceExhausted


class GeminiService(BaseAIProvider):
    # Class-level rate limiting (shared across all instances)
    _last_request_time: float = 0.0
    _rate_limit_lock: Optional[asyncio.Lock] = None
    _lock_creation_lock = threading.Lock()  # Thread-safe lock creation
    _MIN_REQUEST_INTERVAL: float = 6.0  # 6 seconds between requests (10 RPM, safe buffer for 15 RPM limit)

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Safety settings for forensic context
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]

    def _get_lock(self) -> asyncio.Lock:
        """Get or create the rate limit lock for the current event loop (thread-safe)."""
        # Check if we need to recreate the lock for a new event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        with self._lock_creation_lock:
            # If lock doesn't exist or belongs to a different/closed loop, create new one
            if GeminiService._rate_limit_lock is None:
                GeminiService._rate_limit_lock = asyncio.Lock()
            else:
                # Check if the lock's loop is still valid
                try:
                    # Try to check if lock is usable
                    if loop and GeminiService._rate_limit_lock._loop != loop:
                        GeminiService._rate_limit_lock = asyncio.Lock()
                except (AttributeError, RuntimeError):
                    # Lock is from closed loop or corrupted, recreate
                    GeminiService._rate_limit_lock = asyncio.Lock()
            
            return GeminiService._rate_limit_lock

    async def _wait_for_rate_limit(self):
        """Ensure minimum time between requests to avoid quota exceeded errors."""
        lock = self._get_lock()
        
        async with lock:
            now = time.time()
            elapsed = now - GeminiService._last_request_time
            
            if elapsed < self._MIN_REQUEST_INTERVAL:
                wait_time = self._MIN_REQUEST_INTERVAL - elapsed
                print(f"[Rate Limit] Waiting {wait_time:.1f}s before next Gemini request...")
                await asyncio.sleep(wait_time)
            
            # Update timestamp BEFORE releasing lock to prevent race conditions
            GeminiService._last_request_time = time.time()
            print(f"[Rate Limit] Proceeding with Gemini request at {time.strftime('%H:%M:%S')}")

    async def _retry_async(self, func, *args, **kwargs):
        """Retry logic with exponential backoff for quota errors."""
        retries = 3
        
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except ResourceExhausted as e:
                if attempt == retries - 1:
                    raise e
                
                wait_time = 40 * (attempt + 1)  # Exponential backoff: 40s, 80s, 120s
                print(f"Quota exceeded. Retrying in {wait_time}s... (Attempt {attempt + 1}/{retries})")
                await asyncio.sleep(wait_time)
                
                # Reset the rate limit timer after waiting
                GeminiService._last_request_time = time.time()
        
        # This line should never be reached, but for safety
        raise Exception("Retry logic failed unexpectedly")

    async def generate_content(self, prompt: str, model_name: Optional[str] = "gemini-2.0-flash") -> str:
        """
        Generates text content using the specified Gemini model.
        """
        await self._wait_for_rate_limit()
        
        model = genai.GenerativeModel(model_name)
        response = await self._retry_async(
            model.generate_content_async,
            prompt,
            safety_settings=self.safety_settings
        )
        
        return response.text

    async def generate_json(self, prompt: str, model_name: Optional[str] = "gemini-2.0-flash") -> dict:
        """
        Generates structured JSON output. Ensure the prompt asks for JSON.
        """
        await self._wait_for_rate_limit()
        
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = await self._retry_async(
            model.generate_content_async,
            prompt,
            safety_settings=self.safety_settings
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback or retry logic could go here
            return {"error": "Failed to parse JSON", "raw": response.text}

    def _detect_mime_type(self, file_path: str) -> str:
        """Detect MIME type from file extension."""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Default to jpeg if detection fails
        if mime_type is None or not mime_type.startswith('image/'):
            print(f"[Warning] Could not detect image MIME type for {file_path}, defaulting to image/jpeg")
            return 'image/jpeg'
        
        return mime_type

    async def analyze_image(self, image_path: str, prompt: str, model_name: Optional[str] = "gemini-2.0-flash") -> dict:
        """
        Analyzes an image and returns JSON.
        """
        await self._wait_for_rate_limit()
        
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Detect MIME type from file extension
        mime_type = self._detect_mime_type(image_path)
        
        # Load image data with proper cleanup
        try:
            # Import here to avoid circular dependencies if any (though unlikely)
            from app.utils.storage import read_file_content
            image_data = await read_file_content(image_path)
            
            cookie_picture = {
                'mime_type': mime_type,
                'data': image_data
            }
            
            response = await self._retry_async(
                model.generate_content_async,
                [prompt, cookie_picture],
                safety_settings=self.safety_settings
            )
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON", "raw": response.text}
                
        except FileNotFoundError:
            return {"error": f"Image file not found: {image_path}"}
        except Exception as e:
            return {"error": f"Failed to read image: {str(e)}"}