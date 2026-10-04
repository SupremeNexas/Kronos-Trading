import sys
sys.path.append('/Users/supryo/Desktop/Kronos-master')
from webui.db import DatabaseManager

DatabaseManager.init_db()
print("Database initialized successfully.")
