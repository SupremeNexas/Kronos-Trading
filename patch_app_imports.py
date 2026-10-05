with open('webui/app.py', 'r') as f:
    content = f.read()

content = content.replace(
    "from webui.db import DatabaseManager",
    "from webui.db import DatabaseManager, get_db_connection, _adapt_query"
)

with open('webui/app.py', 'w') as f:
    f.write(content)
