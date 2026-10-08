import requests
import os
import time
s = requests.Session()
res = s.post('http://localhost:7070/api/auth/login', json={"email":"demo@kronos.ai", "password":"KronosDemo2026!"})
cookie = res.cookies.get('session_token')
if not cookie:
    for c in res.headers.get('set-cookie', '').split(';'):
        if c.startswith('session_token='):
            cookie = c.split('=', 1)[1]
            break
if cookie:
    s.cookies.set('session_token', cookie)

print(">>> Placing BUY order")
buy = {
    "symbol": "TSLA",
    "side": "BUY",
    "quantity": 1,
    "order_type": "Market",
    "tactic_id": "tactic_breakout",
    "tactic_name": "BREAKOUT",
    "reasoning": "TSLA looks primed",
    "notes": "Testing"
}
buy_res = s.post('http://localhost:7070/api/trading/place-order', json=buy)
print(buy_res.json())

# Need to wait for fill 
time.sleep(4)

print(">>> Syncing (which computes fills)")
s.get('http://localhost:7070/api/trading/trades')

print(">>> Placing SELL order")
sell = {
    "symbol": "TSLA",
    "side": "SELL",
    "quantity": 1,
    "order_type": "Market",
    "tactic_id": "tactic_breakout",
    "tactic_name": "BREAKOUT",
    "reasoning": "Quick flip",
    "notes": "Testing exit"
}
sell_res = s.post('http://localhost:7070/api/trading/place-order', json=sell)
print(sell_res.json())

time.sleep(4)

print(">>> Syncing (which computes fills)")
s.get('http://localhost:7070/api/trading/trades')

perf = s.get('http://localhost:7070/api/tactics/performance')
print(">>> Tactics Performance:")
print(perf.json())

