from abc import ABC, abstractmethod
from typing import Optional


class BaseAIProvider(ABC):
    """
    Abstract base class for AI providers.
    All AI service implementations must inherit from this class.
    """
    
    @abstractmethod
    async def generate_json(self, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Generates structured JSON output from a text prompt.
        
        Args:
            prompt: The input prompt text
            model_name: Optional model name override. If None, uses provider's default.
            
        Returns:
            dict: Parsed JSON response from the model
        """
        pass
    
    @abstractmethod
    async def analyze_image(self, image_path: str, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Analyzes an image with a text prompt and returns structured JSON.
        
        Args:
            image_path: Path to the image file
            prompt: The analysis prompt
            model_name: Optional vision model name override
            
        Returns:
            dict: Parsed JSON response containing image analysis
        """
        pass
    
    async def generate_content(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generates plain text content from a prompt.
        Optional method - providers can override for plain text generation.
        
        Args:
            prompt: The input prompt text
            model_name: Optional model name override
            
        Returns:
            str: Generated text response
        """
        # Default implementation uses generate_json and extracts text
        result = await self.generate_json(prompt, model_name)
        if isinstance(result, dict) and "error" in result:
            return result.get("error", "Unknown error")
        return str(result)
