import google.generativeai as genai
from app.config import settings
from typing import List, Optional
import json
import asyncio
from google.api_core.exceptions import ResourceExhausted

class GeminiService:
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
        
        
    async def _retry_async(self, func, *args, **kwargs):
        retries = 3
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except ResourceExhausted as e:
                if attempt == retries - 1:
                    raise e
                print(f"Quota exceeded. Retrying in 40s... (Attempt {attempt + 1}/{retries})")
                await asyncio.sleep(40) 
        return await func(*args, **kwargs)

    async def generate_content(self, prompt: str, model_name: str = "gemini-2.0-flash") -> str:
        """
        Generates text content using the specified Gemini model.
        """
        model = genai.GenerativeModel(model_name)
        response = await self._retry_async(
            model.generate_content_async,
            prompt,
            safety_settings=self.safety_settings
        )
        return response.text

    async def generate_json(self, prompt: str, model_name: str = "gemini-2.0-flash") -> dict:
        """
        Generates structured JSON output.
        Ensure the prompt asks for JSON.
        """
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

    async def analyze_image(self, image_path: str, prompt: str, model_name: str = "gemini-2.0-flash") -> dict:
        """
        Analyzes an image and returns JSON.
        """
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Load image data
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        cookie_picture = {
            'mime_type': 'image/jpeg', # Detect strictly in real impl
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
