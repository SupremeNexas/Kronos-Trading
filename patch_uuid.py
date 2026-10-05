import re

with open("webui/app.py", "r") as f:
    content = f.read()

content = content.replace(
    "    idempotency_key = data.get('idempotency_key') or f\"m_{uuid.uuid4().hex[:8]}\"",
    "    import uuid\n    idempotency_key = data.get('idempotency_key') or f\"m_{uuid.uuid4().hex[:8]}\""
)

with open("webui/app.py", "w") as f:
    f.write(content)

print("patched")
