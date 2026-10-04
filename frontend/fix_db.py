with open('/Users/supryo/Desktop/Kronos-master/webui/db.py', 'r') as f:
    text = f.read()
text = text.replace(')""",\n,\n\n    """CREATE TABLE IF', ')""",\n    """CREATE TABLE IF')
with open('/Users/supryo/Desktop/Kronos-master/webui/db.py', 'w') as f:
    f.write(text)
