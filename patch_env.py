with open("webui/app.py", "r") as f:
    content = f.read()

head = """import os
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass
"""

content = content.replace("import os", head, 1)

with open("webui/app.py", "w") as f:
    f.write(content)
