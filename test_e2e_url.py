import urllib.request
import urllib.parse
import json
import time

def req(url, data=None, headers=None, method=None):
    if headers is None: headers = {}
    if data:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        if not method: method = 'POST'
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as res:
            cookie = res.getheader('Set-Cookie')
            return res.read().decode('utf-8'), cookie
    except urllib.error.HTTPError as e:
        return e.read().decode('utf-8'), None

# 1. Register
res, c = req('http://127.0.0.1:7070/api/auth/register', {'email': 'e2e3@example.com', 'password': 'password123', 'name': 'E2E'})
print("REGISTER:", res)

# 2. Login
res, cookie = req('http://127.0.0.1:7070/api/auth/login', {'email': 'e2e3@example.com', 'password': 'password123'})
print("LOGIN:", res)

headers = {'Cookie': cookie} if cookie else {}

# 3. Account
res, _ = req('http://127.0.0.1:7070/api/trading/account', headers=headers, method='GET')
print("ACCOUNT:", res[:200])

# 4. Order
res, _ = req('http://127.0.0.1:7070/api/trading/place-order', {
    'symbol': 'AAPL',
    'side': 'buy',
    'quantity': 1,
    'order_type': 'market'
}, headers=headers, method='POST')
print("ORDER:", res)
if '"order_id"' in res: # Try to get alpaca_order_id
    j = json.loads(res)
    print("ALPACA ID:", j.get('order', {}).get('order_id', j.get('order', {}).get('id')))

# 5. Trades
time.sleep(2)
res, _ = req('http://127.0.0.1:7070/api/trading/trades', headers=headers, method='GET')
try:
    j = json.loads(res)
    print("TRADES CNT:", len(j.get('trades', [])))
    if j.get('trades'):
        print("FIRST TRADE:", j['trades'][0])
except:
    print("TRADES RES:", res)
    
