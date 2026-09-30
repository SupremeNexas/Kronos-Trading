import json
import logging

logger = logging.getLogger(__name__)

class BaseLLMProvider:
    def generate_text(self, prompt: str, model: str, system_instruction: str = None) -> str:
        """Query LLM and return raw text response."""
        raise NotImplementedError

    def generate_json(self, prompt: str, model: str, system_instruction: str = None) -> dict:
        """Query LLM and return parsed JSON. Uses heuristics if the model returns markdown-wrapped JSON."""
        # Standard implementation converts output from generate_text to dict
        raw_text = self.generate_text(prompt, model, system_instruction)
        return self._clean_and_parse_json(raw_text)

    def _clean_and_parse_json(self, text: str) -> dict:
        """Clean and parse JSON from markdown-wrapped and text strings."""
        text = text.strip()
        if not text:
            raise ValueError("Empty response received from LLM")

        # Clean markdown wrappers if any
        if text.startswith("```json"):
            text = text[len("```json"):]
        elif text.startswith("```"):
            text = text[len("```"):]

        if text.endswith("```"):
            text = text[:-len("```")]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Try to grab JSON between first '{' and last '}'
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start:end+1])
                except json.JSONDecodeError:
                    pass
            logger.error(f"Failed to parse LLM response as JSON. Raw response: {text}")
            raise ValueError(f"JSON parsing error: {e}") from e
