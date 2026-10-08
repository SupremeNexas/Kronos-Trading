import re

file_path = "frontend/components/Header.tsx"
with open(file_path, "r") as f:
    content = f.read()

# Add SYSTEM PROOF to the NAV_ITEMS without breaking it
if "VERIFICATION" not in content:
    content = content.replace('{ label: "ALERTS", href: "/alerts" }', '{ label: "ALERTS", href: "/alerts" },\n  { label: "VERIFICATION", href: "/verification" }')

with open(file_path, "w") as f:
    f.write(content)
print("Header navigation patched.")
