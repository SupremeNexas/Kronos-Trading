import re
with open("webui/app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "import uuid" in line and not line.startswith("import uuid"):
        continue  # skip indent ones
    if "UnboundLocalError" in line:
        pass
    new_lines.append(line)

with open("webui/app.py", "w") as f:
    f.writelines(new_lines)
