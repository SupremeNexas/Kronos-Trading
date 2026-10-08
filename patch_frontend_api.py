import os

path = "frontend/lib/api.ts"
with open(path, "r") as f:
    content = f.read()

content = content.replace(
    'const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7070";',
    'const API_BASE = "";'
)

with open(path, "w") as f:
    f.write(content)
print("Patched api.ts")
