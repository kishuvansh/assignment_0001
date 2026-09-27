try:
    from src.llm_client import LLMClient
except ImportError:
    from llm_client import LLMClient

class ReplyHandler:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = """You are Vera, magicpin's proactive merchant engagement AI.
You are currently engaged in a conversation with a user (either a merchant or a customer).
Respond to their latest message contextually, naturally, and concisely.
If they ask an out-of-scope question, gently redirect back to the topic.
If they say "yes" or agree to your proposal, provide the direct next step.

Respond ONLY with a JSON object in this format:
{"action": "send", "body": "your message text here", "rationale": "why you chose this response"}
"""

    async def handle_reply(self, merchant: dict, customer: dict, history: list) -> dict:
        # Build prompt from history
        prompt = "CONVERSATION HISTORY:\n"
        for t in history:
            prompt += f"{t['from'].upper()}: {t['msg']}\n"
            
        prompt += "\nMERCHANT CONTEXT:\n" + str(merchant)
        if customer:
            prompt += "\nCUSTOMER CONTEXT:\n" + str(customer)
            
        prompt += "\n\nDraft the next response."
        
        response_text = await self.llm.complete(prompt, system=self.system_prompt, json_format=True)
        
        import json
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```json"): clean_text = clean_text[7:]
            if clean_text.startswith("```"): clean_text = clean_text[3:]
            if clean_text.endswith("```"): clean_text = clean_text[:-3]
            data = json.loads(clean_text)
            return data
        except Exception as e:
            print("Reply error parsing", e, response_text)
            return {"action": "send", "body": "Got it.", "rationale": "fallback"}
