with open("webui/app.py", "r") as f:
    text = f.read()

text = text.replace(
"""        try:
            from webui.db import get_db_connection, _adapt_query
            import uuid
            conn, _ = get_db_connection()""",
"""        try:
            from webui.db import get_db_connection, _adapt_query
            conn, _ = get_db_connection()"""
)

if "import uuid" not in text[:500]:
    text = "import uuid\n" + text

with open("webui/app.py", "w") as f:
    f.write(text)
