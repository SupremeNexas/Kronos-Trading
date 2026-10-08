with open("webui/app.py", "r") as f:
    content = f.read()

bad = "    import datetime, json\nimport uuid\n\n    try:\n        try:"
good = "    import datetime, json\n    import uuid\n\n    try:\n        try:"
content = content.replace(bad, good)

with open("webui/app.py", "w") as f:
    f.write(content)
