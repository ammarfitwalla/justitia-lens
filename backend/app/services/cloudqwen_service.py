import aiohttp
import json
import base64
from typing import Optional
from app.config import settings
from app.services.base_provider import BaseAIProvider
from PIL import Image
import io
import asyncio


class CloudQwenService(BaseAIProvider):
    """
    CloudQwen API integration for multimodal AI capabilities.
    Supports both text generation and vision analysis.
    """
    
    def __init__(self):
        self.api_key = settings.CLOUDQWEN_API_KEY
        self.base_url = settings.CLOUDQWEN_BASE_URL
        self.model = settings.CLOUDQWEN_MODEL
        self.vision_model = settings.CLOUDQWEN_VISION_MODEL
        
    async def generate_json(self, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Generates structured JSON output using CloudQwen API.
        """
        url = f"{self.base_url}/chat/completions"
        model = model_name or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Instruct model to return JSON
        full_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON."
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that always returns valid JSON responses."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "error": f"CloudQwen API Error: {response.status} - {error_text}"
                        }
                    
                    data = await response.json()
                    
                    # Extract content from response
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            return {
                                "error": "Failed to parse JSON from CloudQwen",
                                "raw": content
                            }
                    else:
                        return {
                            "error": "No response choices from CloudQwen",
                            "raw": str(data)
                        }
                        
        except Exception as e:
            return {"error": f"CloudQwen Connection Failed: {str(e)}"}
    
    async def analyze_image(self, image_path: str, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Analyzes an image using CloudQwen's multimodal vision model.
        """
        url = f"{self.base_url}/chat/completions"
        model = model_name or self.vision_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Read and encode image with compression if needed
        try:
            # CloudQwen has a 10MB limit for base64 images
            MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
            
            # First, try to read the original image
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
            
            # Check if we need to compress
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            if len(base64_data) > MAX_SIZE_BYTES:
                print(f"Image too large ({len(base64_data)} bytes), compressing...")
                
                # Open with PIL and compress
                img = Image.open(image_path)
                
                # Convert RGBA to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                
                # Resize image to reduce size
                # Start with 80% quality and reduce dimensions if needed
                quality = 80
                max_dimension = 2048
                
                while True:
                    # Resize if larger than max_dimension
                    if img.width > max_dimension or img.height > max_dimension:
                        ratio = min(max_dimension / img.width, max_dimension / img.height)
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                    else:
                        resized_img = img
                    
                    # Save to bytes with compression
                    buffer = io.BytesIO()
                    resized_img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    compressed_bytes = buffer.getvalue()
                    
                    # Check size
                    base64_data = base64.b64encode(compressed_bytes).decode('utf-8')
                    
                    if len(base64_data) <= MAX_SIZE_BYTES:
                        print(f"Compressed to {len(base64_data)} bytes (quality={quality}, size={resized_img.size})")
                        break
                    
                    # Try reducing quality or dimensions
                    if quality > 50:
                        quality -= 10
                    elif max_dimension > 1024:
                        max_dimension = int(max_dimension * 0.8)
                    else:
                        # If we still can't compress enough, give up
                        print(f"Warning: Could not compress image below 10MB limit")
                        break
                
                image_data = base64_data
            else:
                image_data = base64_data
                
        except Exception as e:
            return {"error": f"Failed to read/encode image: {str(e)}"}
        
        # Determine image MIME type (basic detection)
        mime_type = "image/jpeg"
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif image_path.lower().endswith(".webp"):
            mime_type = "image/webp"
        
        full_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON."
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful vision assistant that always returns valid JSON responses."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        
        # Retry logic for transient errors
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
                        error_text = await response.text()
                        
                        if response.status != 200:
                            print(f"CloudQwen Vision API Error (attempt {attempt + 1}/{max_retries + 1}): {response.status} - {error_text}")
                            
                            # Retry on 401 or 500 errors
                            if response.status in [401, 500, 503] and attempt < max_retries:
                                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                                continue
                            
                            return {
                                "error": f"CloudQwen Vision Error: {response.status} - {error_text}"
                            }
                        
                        data = await response.json()
                        
                        # Extract content from response
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0]["message"]["content"]
                            
                            try:
                                return json.loads(content)
                            except json.JSONDecodeError:
                                return {
                                    "error": "Failed to parse JSON from CloudQwen Vision",
                                    "raw": content
                                }
                        else:
                            return {
                                "error": "No response choices from CloudQwen Vision",
                                "raw": str(data)
                            }
                            
            except aiohttp.ClientError as e:
                print(f"CloudQwen Vision Connection Error (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                if attempt < max_retries:
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                return {"error": f"CloudQwen Vision Connection Failed: {str(e)}"}
            except Exception as e:
                print(f"CloudQwen Vision Unexpected Error (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                if attempt < max_retries:
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
        
        return {"error": "CloudQwen Vision Failed after all retries"}
    
    async def generate_content(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generates plain text content using CloudQwen.
        """
        url = f"{self.base_url}/chat/completions"
        model = model_name or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"CloudQwen Error: {response.status} - {error_text}"
                    
                    data = await response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        return f"CloudQwen Error: No response choices"
                        
        except Exception as e:
            return f"CloudQwen Connection Failed: {str(e)}"
