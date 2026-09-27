import os
try:
    from dotenv import load_dotenv
    # Load standard .env if present
    load_dotenv()
except ImportError:
    pass

# System Configs
AI_PROVIDER = os.getenv("TRADINGAGENTS_LLM_PROVIDER", "openai").lower() # DEFAULT: openai
AI_DEEP_MODEL = os.getenv("TRADINGAGENTS_DEEP_THINK_LLM", "gpt-4o")
AI_QUICK_MODEL = os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", "gpt-4o-mini")

# Provider API Keys/Endpoints
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Execution settings
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "3"))
AI_MAX_CONCURRENT_AGENTS = int(os.getenv("AI_MAX_CONCURRENT_AGENTS", "4"))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "4096"))

# Trading Risk settings
GLOBAL_KILL_SWITCH = False
MAX_CASH_ALLOCATION_PERCENT = 50.0  # Cap on cash used for a single trade

# Directory setup
RESULTS_DIR = os.getenv("TRADINGAGENTS_RESULTS_DIR", os.path.join(os.path.expanduser("~"), ".tradingagents", "logs"))
CACHE_DIR = os.getenv("TRADINGAGENTS_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".tradingagents", "cache"))
MEMORY_LOG_PATH = os.path.join(RESULTS_DIR, "trading_memory.json")
CHECKPOINT_DB_PATH = os.path.join(CACHE_DIR, "checkpoints", "agent_runs.db")

# Model configurations
MODEL_ROUTING = {
    "technical": {"provider": AI_PROVIDER, "model": AI_QUICK_MODEL},
    "fundamental": {"provider": AI_PROVIDER, "model": AI_DEEP_MODEL},
    "news": {"provider": AI_PROVIDER, "model": AI_QUICK_MODEL},
    "sentiment": {"provider": AI_PROVIDER, "model": AI_QUICK_MODEL},
    "quant": {"provider": AI_PROVIDER, "model": AI_QUICK_MODEL},
    "macro": {"provider": AI_PROVIDER, "model": AI_QUICK_MODEL},
    "debate": {"provider": AI_PROVIDER, "model": AI_DEEP_MODEL},
    "trader": {"provider": AI_PROVIDER, "model": AI_DEEP_MODEL},
    "portfolio": {"provider": AI_PROVIDER, "model": AI_DEEP_MODEL},
}
