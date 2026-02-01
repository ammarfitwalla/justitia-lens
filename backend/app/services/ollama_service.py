import aiohttp
import json
import base64
from app.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.vision_model = settings.OLLAMA_VISION_MODEL
        
    async def generate_json(self, prompt: str, model_name: str = None) -> dict:
        """
        Generates structured JSON output using Ollama.
        """
        url = f"{self.base_url}/generate"
        model = model_name or self.model
        
        # Llama 3 specific instruction for JSON
        full_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON."

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json" 
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        return {"error": f"Ollama Error: {response.status} - {await response.text()}"}
                    
                    data = await response.json()
                    response_text = data.get("response", "")
                    
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse JSON from Ollama", "raw": response_text}
                        
        except Exception as e:
            return {"error": f"Ollama Connection Failed: {str(e)}"}

    async def analyze_image(self, image_path: str, prompt: str) -> dict:
        """
        Analyzes an image using a multimodal model (e.g., Llava) via Ollama.
        """
        url = f"{self.base_url}/generate"
        
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            return {"error": f"Failed to read/encode image: {str(e)}"}

        full_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON."
        
        payload = {
            "model": self.vision_model,
            "prompt": full_prompt,
            "images": [encoded_string],
            "stream": False,
            "format": "json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        return {"error": f"Ollama Vision Error: {response.status} - {await response.text()}"}
                    
                    data = await response.json()
                    response_text = data.get("response", "")
                    
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                         # Sometimes Llava is chatty even with JSON constraints
                        return {"error": "Failed to parse JSON from Ollama Vision", "raw": response_text}
                        
        except Exception as e:
            return {"error": f"Ollama Vision Connection Failed: {str(e)}"}
