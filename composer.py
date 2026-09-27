import json
try:
    from src.llm_client import LLMClient
    from src.prompt_templates import SYSTEM_PROMPT, build_composer_prompt
except ImportError:
    from llm_client import LLMClient
    from prompt_templates import SYSTEM_PROMPT, build_composer_prompt

class Composer:
    def __init__(self):
        self.llm = LLMClient()

    async def compose(self, category: dict, merchant: dict, trigger: dict, customer: dict = None) -> dict:
        prompt = build_composer_prompt(category, merchant, trigger, customer)
        
        response_text = await self.llm.complete(prompt, system=SYSTEM_PROMPT, json_format=True)
        
        # Parse the JSON response
        try:
            # Sometime LLMs still output backticks even with json_format
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            data = json.loads(clean_text)
            
            message = data.get("body") or data.get("message") or "Hello from Vera!"
            rationale = data.get("rationale", "Contextually generated engagement message.")
            cta = data.get("cta", "open_ended")
            
            return {
                "body": message,
                "rationale": rationale,
                "cta": cta
            }
        except Exception as e:
            print(f"Failed to parse LLM response: {e}. Raw: {response_text}")
            return {
                "body": "Hi there! I noticed some updates to your profile.",
                "rationale": "Fallback message due to parsing error.",
                "cta": "open_ended"
            }
