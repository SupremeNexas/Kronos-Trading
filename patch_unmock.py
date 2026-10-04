import os

with open('webui/app.py', 'r') as f:
    content = f.read()

# Replace the specific hard-override lines
old_section = """        # Hard-override to mock to prevent HF timeouts/OOM on 512MB free tier
        forecast_mode = os.environ.get("FORECAST_MODE", "mock").lower()
        if os.environ.get("RENDER"):
            forecast_mode = "mock"
            
        if MODEL_AVAILABLE and forecast_mode == "ai":"""

new_section = """        forecast_mode = os.environ.get("FORECAST_MODE", "mock").lower()
        if MODEL_AVAILABLE and forecast_mode == "ai":"""

content = content.replace(old_section, new_section)

with open('webui/app.py', 'w') as f:
    f.write(content)
