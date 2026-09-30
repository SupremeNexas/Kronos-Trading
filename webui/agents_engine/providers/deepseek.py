import requests
import os
import logging
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class DeepSeekProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, model: str, system_instruction: str = None) -> str:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY env variable not set")

        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code != 200:
                raise ValueError(f"DeepSeek API error {response.status_code}: {response.text}")

            res_json = response.json()
            return res_json["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error querying DeepSeek: {e}")
            raise
