from app.services.model_factory import get_provider
from app import schemas
import json

class AgentSynthesizer:
    def __init__(self):
        # Factory automatically selects provider based on settings.AI_PROVIDER
        self.llm = get_provider()

    async def detect_discrepancies(self, narrative: schemas.NarrativeAnalysisResult, vision: schemas.VisionAnalysisResult) -> dict:
        """
        Compares Narrative Claims vs. Visual Observations to find inconsistencies.
        """
        # Prepare inputs for the prompt
        narrative_json = narrative.model_dump_json()
        vision_json = vision.model_dump_json()
        
        prompt = f"""
        You are an Adversarial Forensic Editor. Your job is to comparing a Police Report Narrative against Objective Visual Evidence.
        
        INPUT DATA:
        1. Narrative Claims (Timeline of assertions):
        {narrative_json}
        
        2. Visual Observations (Objective facts from images):
        {vision_json}
        
        TASK:
        Identify "Discovery Points" where the Visual Evidence **CONTRADICTS** or **FAIL TO SUPPORT** the Narrative Claim.
        
        RULES:
        1.  **Direct Contradictions**: Report says "Gun", Image says "Phone". (HIGH PRIORITY)
        2.  **Omissions**: Report says "Suspect punched officer", Image shows suspect hands at sides. (MEDIUM PRIORITY)
        3.  **Ambiguity**: If visual confidence is LOW, do not flag as a contradiction.
        
        Output JSON:
        {{
            "discrepancies": [
                {{
                    "timestamp_ref": "04:20",
                    "clean_claim": "Suspect produced a black firearm",
                    "visual_fact": "Suspect held a black rectangular object (likely phone)",
                    "description": "Object misidentification. Visual evidence does not support firearm.",
                    "status": "FLAGGED"
                }}
            ]
        }}
        """
        
        try:
            # Use provider's default model (configured in settings)
            return await self.llm.generate_json(prompt)
        except Exception as e:
            return {"error": str(e), "discrepancies": []}
