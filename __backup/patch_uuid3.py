with open("webui/app.py", "r") as f:
    text = f.read()

import re
# Remove any local 'import uuid'
text = re.sub(r"^[ \t]+import uuid\n", "", text, flags=re.MULTILINE)
# Also just in case there's multiple on one line
text = text.replace("import uuid, ", "import ")

with open("webui/app.py", "w") as f:
    f.write(text)

