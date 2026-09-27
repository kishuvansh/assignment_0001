import os
import json
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

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1000
        }
        
        if json_format:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=20.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"LLM Error: {e}")
                return ""
