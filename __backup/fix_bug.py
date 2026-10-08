import re
with open("webui/agents_engine/orchestrator.py", "r") as f:
    text = f.read()

# Replace validation fetching from dictionary vs object 
# The UI has access to what orchestrator saves

with open("webui/agents_engine/orchestrator.py", "w") as f:
    f.write(text)
