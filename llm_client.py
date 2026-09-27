import os
import json
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.model = model or os.environ.get("OPENROUTER_MODEL", "openrouter/free")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def complete(self, prompt: str, system: str = None, json_format: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://magicpin.com",
            "X-Title": "magicpin Challenge Bot"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        models_to_try = [self.model, "google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free"]
        
        async with httpx.AsyncClient() as client:
            for model_name in models_to_try:
                for attempt in range(2):
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 1000
                    }
                    
                    try:
                        response = await client.post(
                            self.base_url,
                            headers=headers,
                            json=payload,
                            timeout=45.0
                        )
                        if response.status_code == 200:
                            data = response.json()
                            choices = data.get("choices", [])
                            if choices and choices[0].get("message", {}).get("content"):
                                content = choices[0]["message"]["content"].strip()
                                if content and content != "None" and "User Safety: safe" not in content:
                                    return content
                        elif response.status_code == 429:
                            await asyncio.sleep(2)
                    except Exception as e:
                        pass
                    await asyncio.sleep(1)
                    
        return ""
