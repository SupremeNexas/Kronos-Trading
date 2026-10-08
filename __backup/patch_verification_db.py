import re

with open("webui/verification_routes.py", "r") as f:
    content = f.read()

content = content.replace("db.IS_POSTGRES", "IS_POSTGRES")
content = content.replace("with db.get_connection()", "with get_db_connection()[0]")

with open("webui/verification_routes.py", "w") as f:
    f.write(content)

print("Fixed verification_routes.py imports")
