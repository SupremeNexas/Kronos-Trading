with open("webui/app.py", "r") as f:
    text = f.read()

text = text.replace("execution_time", "submitted_at")

with open("webui/app.py", "w") as f:
    f.write(text)

