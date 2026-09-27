import requests
import os
import logging
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, model: str, system_instruction: str = None) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY env variable not set")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_instruction:
            payload["system"] = system_instruction

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code != 200:
                raise ValueError(f"Anthropic API error {response.status_code}: {response.text}")

            res_json = response.json()
            return res_json["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error querying Anthropic: {e}")
            raise
