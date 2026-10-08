with open("webui/app.py", "r") as f:
    text = f.read()

text = text.replace("\"completed\", datetime.now().isoformat()", "\"filled\", datetime.now().isoformat()")

with open("webui/app.py", "w") as f:
    f.write(text)

