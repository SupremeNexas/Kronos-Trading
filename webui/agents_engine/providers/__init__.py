from .base import BaseLLMProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from .deepseek import DeepSeekProvider
from .ollama import OllamaProvider

def get_provider(provider_name: str) -> BaseLLMProvider:
    provider_name = provider_name.strip().lower()
    if provider_name == "openai":
         return OpenAIProvider()
    elif provider_name == "anthropic":
         return AnthropicProvider()
    elif provider_name == "gemini" or provider_name == "google":
         return GeminiProvider()
    elif provider_name == "deepseek":
         return DeepSeekProvider()
    elif provider_name == "ollama":
         return OllamaProvider()
    else:
         raise ValueError(f"Unsupported LLM provider: {provider_name}")
