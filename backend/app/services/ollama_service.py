import json
import base64
import asyncio
import re
from typing import Optional
from ollama import Client
from app.config import settings
from app.services.base_provider import BaseAIProvider


class OllamaService(BaseAIProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.vision_model = settings.OLLAMA_VISION_MODEL
        self.api_key = settings.OLLAMA_API_KEY  # For Ollama cloud
        self._client = None
    
    def _get_client(self) -> Client:
        """Get Ollama client configured for cloud API."""
        if self._client is None:
            if self.api_key:
                self._client = Client(
                    host=self.base_url,
                    headers={'Authorization': 'Bearer ' + self.api_key}
                )
            else:
                # Fallback to local if no API key
                self._client = Client(host="http://localhost:11434")
        return self._client
    
    def _extract_json_from_text(self, text: str) -> dict:
        """Extract JSON from LLM response, handling markdown fences and cleanup."""
        # Remove thinking tags if present
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        
        # Try to find fenced JSON block
        fenced = re.search(r"```json(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if fenced:
            text = fenced.group(1).strip()
        else:
            # Try generic code fence
            fenced = re.search(r"```(.*?)```", text, re.DOTALL)
            if fenced:
                text = fenced.group(1).strip()

        # Find JSON object boundaries
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            text = text[first:last + 1]

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Cleanup common issues
            text = re.sub(r",\s*}", "}", text)
            text = re.sub(r",\s*]", "]", text)
            text = re.sub(r"'", '"', text)  # Single to double quotes
            return json.loads(text)
        
    async def generate_json(self, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Generates structured JSON output using Ollama.
        """
        model = model_name or self.model
        full_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON."

        try:
            client = self._get_client()
            # Run sync client in thread pool for async compatibility
            response = await asyncio.to_thread(
                client.chat,
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                options={"temperature": 0}
            )
            
            response_text = response['message']['content']
            
            try:
                return self._extract_json_from_text(response_text)
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON from Ollama", "raw": response_text}
                        
        except Exception as e:
            return {"error": f"Ollama Connection Failed: {str(e)}"}

    async def analyze_image(self, image_path: str, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Analyzes an image using a multimodal model (e.g., Llava, Qwen2-VL) via Ollama.
        """
        vision_model = model_name or self.vision_model
        
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            return {"error": f"Failed to read/encode image: {str(e)}"}

        full_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON."

        try:
            client = self._get_client()
            # Run sync client in thread pool for async compatibility
            response = await asyncio.to_thread(
                client.chat,
                model=vision_model,
                messages=[{
                    "role": "user",
                    "content": full_prompt,
                    "images": [encoded_string]
                }],
                options={"temperature": 0}
            )
            
            response_text = response['message']['content']
            
            try:
                return self._extract_json_from_text(response_text)
            except json.JSONDecodeError:
                # Sometimes vision models are chatty even with JSON constraints
                return {"error": "Failed to parse JSON from Ollama Vision", "raw": response_text}
                        
        except Exception as e:
            return {"error": f"Ollama Vision Connection Failed: {str(e)}"}

