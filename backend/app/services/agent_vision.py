from app.services.gemini_service import GeminiService
from app.config import settings
import json

class AgentVision:
    def __init__(self):
        self.gemini = GeminiService()

    async def analyze_evidence(self, image_path: str) -> dict:
        """
        Analyzes an image for forensic discovery points with strict guardrails.
        """
        prompt = """
        You are a Forensic Visual Analyst. Analyze this image for objective discovery points.
        
        STRICT RULES:
        1.  **Do NOT infer intent**, threat level, or emotional state. Describe only what is visually observable.
        2.  **Object Identification**: If an object is not clearly identifiable, describe its shape/color/material (e.g., "Black rectangular object") rather than guessing specific models (e.g., "iPhone 13").
        3.  **Confidence**: You must assign a confidence level (LOW, MEDIUM, HIGH) to every observation.
            -   If lighting is poor, handling is fast, or object is partially occluded, confidence must be LOW or MEDIUM.
            -   HIGH confidence is reserved for clear, unobstructed views.
        4.  **Timestamps**: Even though this is a static image, output a "timestamp_ref" field (e.g. "00:00:00" or similar placeholder) to maintain schema compatibility with video analysis.
        
        Identify:
        1. Objects held (Any object. If unknown, describe properties).
        2. Clothing and visible attributes.
        3. Lighting conditions.
        4. Procedural markers.
        
        Return JSON:
        {
            "observations": [
                {
                    "timestamp_ref": "00:00:00",
                    "category": "OBJECT",
                    "entity": "Suspect",
                    "label": "Unknown object",
                    "confidence": "MEDIUM",
                    "details": "Black rectangular object held in right hand, reflective surface visible"
                },
                {
                    "timestamp_ref": "00:00:00",
                    "category": "ENVIRONMENT",
                    "entity": "Scene",
                    "label": "Night",
                    "confidence": "HIGH",
                    "details": "Street lighting visible, dark sky"
                }
            ]
        }
        """
        
        try:
            return await self.gemini.analyze_image(image_path, prompt, model_name="gemini-1.5-pro-latest")
        except Exception as e:
            # Fallback for JSON parsing or API errors
            return {"error": str(e), "observations": []}
