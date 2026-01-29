import google.generativeai as genai
from app.config import settings
from typing import List, Optional
import json

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
        
    async def generate_content(self, prompt: str, model_name: str = "gemini-1.5-flash-latest") -> str:
        """
        Generates text content using the specified Gemini model.
        """
        model = genai.GenerativeModel(model_name)
        response = await model.generate_content_async(
            prompt,
            safety_settings=self.safety_settings
        )
        return response.text

    async def generate_json(self, prompt: str, model_name: str = "gemini-1.5-flash-latest") -> dict:
        """
        Generates structured JSON output.
        Ensure the prompt asks for JSON.
        """
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        response = await model.generate_content_async(
            prompt,
            safety_settings=self.safety_settings
        )
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback or retry logic could go here
            return {"error": "Failed to parse JSON", "raw": response.text}

    async def analyze_image(self, image_path: str, prompt: str, model_name: str = "gemini-1.5-pro-latest") -> dict:
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

        response = await model.generate_content_async(
            [prompt, cookie_picture],
            safety_settings=self.safety_settings
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
             return {"error": "Failed to parse JSON", "raw": response.text}
