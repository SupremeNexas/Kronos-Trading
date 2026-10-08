import sys

with open("webui/app.py", "r") as f:
    content = f.read()

old_block = """        if MODEL_AVAILABLE and os.environ.get("FORECAST_MODE", "mock").lower() == "ai":"""
new_block = """        # Hard-override to mock to prevent HF timeouts/OOM on 512MB free tier
        forecast_mode = os.environ.get("FORECAST_MODE", "mock").lower()
        if os.environ.get("RENDER"):
            forecast_mode = "mock"
            
        if MODEL_AVAILABLE and forecast_mode == "ai":"""

content = content.replace(old_block, new_block)

with open("webui/app.py", "w") as f:
    f.write(content)
