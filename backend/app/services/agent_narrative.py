from app.services.gemini_service import GeminiService
from app.services.ollama_service import OllamaService
from app.services.pdf_service import PDFService
from app.config import settings
import json

class AgentNarrative:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        if self.provider == "ollama":
            self.llm = OllamaService()
        else:
            self.llm = GeminiService()
    
    async def extract_claims(self, text: str) -> dict:
        """
        Analyzes narrative text to extract factual claims.
        """
        # ... prompt construction remains ...
        prompt = f"""
        You are a Forensic Narrative Analyst. Extract a chronological timeline of OBJECTIVE FACTUAL ASSERTIONS from the police report.
        
        STRICT RULES:
        1.  **Objective Only**: Ignore subjective statements like "He looked aggressive". Record physical actions only.
        2.  **Certainty**: Assign a certainty level (EXPLICIT, IMPLIED) to each claim.
            -   EXPLICIT: "I saw him pull a gun."
            -   IMPLIED: "Movement consistent with reaching for a waistband." (describe the movement, not the intent).
        
        Return JSON format:
        {{
            "timeline": [
                {{
                    "timestamp_ref": "04:20", 
                    "entity": "Suspect", 
                    "action": "produced", 
                    "object": "black firearm", 
                    "certainty": "EXPLICIT",
                    "description": "Suspect produced a black firearm from waistband"
                }}
            ]
        }}
        
        REPORT TEXT:
        {text}
        """
        
        try:
            if self.provider == "ollama":
                return await self.llm.generate_json(prompt)
            else:
                 return await self.llm.generate_json(prompt, model_name="gemini-2.0-flash")
        except Exception as e:
            import traceback
            print("Error in extract_claims:")
            traceback.print_exc()
            return {"error": str(e), "timeline": []}

    async def process_report(self, file_path: str) -> dict:
        try:
            text = PDFService.extract_text(file_path)
            return await self.extract_claims(text)
        except Exception as e:
            import traceback
            print(f"Error in process_report for file {file_path}:")
            traceback.print_exc()
            return {"error": str(e)}
