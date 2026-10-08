with open("webui/agents_engine/orchestrator.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "def _simulate_predictions" in line:
        # fix it to 4 spaces
        lines[i] = "    " + line.lstrip()

with open("webui/agents_engine/orchestrator.py", "w") as f:
    f.writelines(lines)
