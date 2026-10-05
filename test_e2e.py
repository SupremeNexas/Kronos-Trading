import requests
import json
import time

s = requests.Session()

# 1. Register
reg_res = s.post('http://127.0.0.1:7070/api/register', json={
    'email': 'e2e@example.com',
    'password': 'password123',
    'name': 'E2E Test'
})
print("REGISTER:", reg_res.json())

# 2. Login
log_res = s.post('http://127.0.0.1:7070/api/login', json={
    'email': 'e2e@example.com',
    'password': 'password123'
})
print("LOGIN:", log_res.json())

# 3. /api/trading/account
act_res = s.get('http://127.0.0.1:7070/api/trading/account')
print("ACCOUNT:", act_res.text[:100])

# 4. Place Order
order_res = s.post('http://127.0.0.1:7070/api/trading/place-order', json={
    'symbol': 'AAPL',
    'side': 'buy',
    'quantity': 1,
    'order_type': 'market'
})
print("ORDER:", order_res.text)

# 5. Check Trades
time.sleep(2)
trades_res = s.get('http://127.0.0.1:7070/api/trading/trades')
print("TRADES:", trades_res.text)

