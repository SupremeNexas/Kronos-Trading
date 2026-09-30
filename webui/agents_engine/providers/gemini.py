import requests
import os
import logging
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, model: str, system_instruction: str = None) -> str:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY env variable not set")

        # Map typical model aliases if needed. e.g. "gemini-2.5-pro" or similar
        model_name = model
        if not model_name.startswith("models/"):
            # Ensure model starts with models/ for url structure
            if "gemini" in model_name:
                model_name = f"models/{model_name}"

        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code != 200:
                raise ValueError(f"Gemini API error {response.status_code}: {response.text}")

            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Error querying Gemini: {e}")
            raise
