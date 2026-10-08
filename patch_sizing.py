import os

path = "webui/agents_engine/strategy_utils/sizing.py"
with open(path, "r") as f:
    content = f.read()

content = content.replace("from scripts import risk_constants as rc", "from . import risk_constants as rc")
content = content.replace("from scripts.risk_constants import", "from .risk_constants import")

with open(path, "w") as f:
    f.write(content)
print("Patched sizing.py")
