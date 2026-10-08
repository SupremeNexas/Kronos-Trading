with open("webui/app.py", "r") as f:
    lines = f.readlines()

run_lines = []
new_lines = []

in_run = False
for line in lines:
    if "def run_server(" in line:
        in_run = True
    
    if in_run:
        run_lines.append(line)
        if "app.run" in line:
            in_run = False
            # add a few empty lines and stop capturing run_lines, but wait, run_server was defined somewhere.
            # let's be more precise.

