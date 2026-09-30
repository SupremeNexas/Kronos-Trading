import requests
import os
import logging
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, model: str, system_instruction: str = None) -> str:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip('/')
        url = f"{base_url}/api/generate"

        full_prompt = prompt
        if system_instruction:
            full_prompt = f"System Instruction: {system_instruction}\n\nUser: {prompt}"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code != 200:
                raise ValueError(f"Ollama API error {response.status_code}: {response.text}")

            res_json = response.json()
            return res_json.get("response", "").strip()
        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            raise RuntimeError(f"Ollama connection error: {e}") from e
