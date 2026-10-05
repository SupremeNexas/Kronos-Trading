import urllib.request
import json
import urllib.error
import time

payload = {
    "symbol": "BTC",
    "side": "BUY",
    "quantity": 1,
    "order_type": "Market",
    "price": 60000.0,
    "strategy": "EARLY_SIGNAL_SCANNER",
    "signal_scan_id": "testsuite-uuid-1234",
    "signal_score": 3,
    "volume_ratio": "2.5",
    "attention_score": "2",
    "momentum_7d": "10.0",
    "decision": "MANUAL_TRADE"
}

req = urllib.request.Request("http://127.0.0.1:7070/api/trading/place-order", 
                             data=json.dumps(payload).encode('utf-8'),
                             headers={'Content-Type': 'application/json'},
                             method="POST")

retries = 5
while retries > 0:
    try:
        with urllib.request.urlopen(req) as response:
            print("DB RESPONSE:", response.read().decode('utf-8'))
        break
    except urllib.error.HTTPError as e:
        print("Error HTTP:", e.read().decode('utf-8'))
        break
    except urllib.error.URLError as e:
        print("Waiting for server...", e)
        time.sleep(1)
        retries -= 1

# Check if it was persisted to the database
from webui.db import get_db_connection
conn, _ = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM scanner_trades WHERE signal_scan_id = 'testsuite-uuid-1234'")
rows = cursor.fetchall()
print("SCANNER TRADES DB ROWS:", len(rows))
if rows:
    print(rows[0])
conn.close()

