import requests
import json
import time

s = requests.Session()

# 1. We mock the cookie or login if necessary?
# With local bypass, any API should work.
# Wait, local bypass sets the user based on LOCAL_TRADING_MODE.
print("Triggering E2E Demo...")
r = s.post("http://localhost:7070/api/trading/e2e-demo")
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    print(r.status_code, r.text)
    
