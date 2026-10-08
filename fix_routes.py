with open("webui/app.py", "r") as f:
    content = f.read()

# We can find `if __name__ == '__main__':`
# Split the content and move all routes after it to before it.
parts = content.split("if __name__ == '__main__':")
if len(parts) == 2:
    upper = parts[0]
    lower = parts[1]
    
    # But lower contains app.run() and also some routes. Let's find "app.run"
    app_run_idx = lower.find("app.run")
    # let's split the lower part by app.run line
    lower_lines = lower.split("\n")
    run_idx = -1
    for i, line in enumerate(lower_lines):
        if "app.run" in line:
            run_idx = i
            break
            
    after_run = "\n".join(lower_lines[run_idx+1:])
    before_run = "\n".join(lower_lines[:run_idx+1])
    
    new_content = upper + after_run + "\nif __name__ == '__main__':\n" + before_run
    with open("webui/app.py", "w") as f:
        f.write(new_content)

