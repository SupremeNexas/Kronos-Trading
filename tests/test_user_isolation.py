import pytest
import sqlite3
import os
import uuid
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webui.app import app
from webui.db import DatabaseManager, get_db_connection, _adapt_query

@pytest.fixture(scope="module")
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="module")
def users(client):
    u1_email = f"user1_{uuid.uuid4().hex[:6]}@test.com"
    u2_email = f"user2_{uuid.uuid4().hex[:6]}@test.com"
    pwd = "password123"
    
    DatabaseManager.create_user(u1_email, pwd, "User 1")
    DatabaseManager.create_user(u2_email, pwd, "User 2")
    
    res_a = client.post('/api/auth/login', json={"email": u1_email, "password": pwd})
    token_a = res_a.headers.get('Set-Cookie').split(';')[0].split('=')[1]
    
    res_b = client.post('/api/auth/login', json={"email": u2_email, "password": pwd})
    token_b = res_b.headers.get('Set-Cookie').split(';')[0].split('=')[1]
    
    return {
        "A": {"email": u1_email, "token": token_a, "id": res_a.get_json()['user']['id']},
        "B": {"email": u2_email, "token": token_b, "id": res_b.get_json()['user']['id']}
    }

def test_watchlist_isolation(client, users):
    sym = f"TST_{uuid.uuid4().hex[:4]}".upper()
    client.post('/api/watchlist', json={"symbol": sym}, headers={'Cookie': f"session_token={users['A']['token']}"})
    
    res_b = client.get('/api/watchlist', headers={'Cookie': f"session_token={users['B']['token']}"})
    items_b = res_b.get_json().get('watchlists', [])
    assert not any(w.get('items') and w['items'][0]['symbol'] == sym for w in items_b)

def test_scanner_isolation(client, users):
    conn, _ = get_db_connection()
    c = conn.cursor()
    sid = f"scan_{uuid.uuid4().hex[:6]}"
    c.execute(_adapt_query("INSERT INTO scanner_history (user_id, signal_scan_id, asset) VALUES (?, ?, ?)"), (users['A']['id'], sid, 'TSLA'))
    conn.commit()
    conn.close()
    
    res_b = client.get('/api/scanner/history', headers={'Cookie': f"session_token={users['B']['token']}"})
    assert sid not in str(res_b.data)

def test_forecast_isolation(client, users):
    conn, _ = get_db_connection()
    c = conn.cursor()
    fid = f"pred_{uuid.uuid4().hex[:6]}"
    c.execute(_adapt_query("INSERT INTO prediction_runs (id, user_id, run_id, symbol, timeframe, forecast_horizon) VALUES (?, ?, ?, ?, ?, ?)"), 
              (fid, users['A']['id'], 'run_a', 'AMZN', '1D', 14))
    conn.commit()
    conn.close()
    
    res_b = client.get('/api/forecast-history', headers={'Cookie': f"session_token={users['B']['token']}"})
    assert fid not in str(res_b.data)

def test_trades_isolation(client, users):
    conn, _ = get_db_connection()
    c = conn.cursor()
    oid = f"ord_{uuid.uuid4().hex[:6]}"
    try:
        c.execute(_adapt_query("INSERT INTO orders (id, portfolio_id, symbol, side, order_type, quantity) VALUES (?, (SELECT id FROM portfolios WHERE user_id = ? LIMIT 1), ?, ?, ?, 10.0)"), 
                (oid, users['A']['id'], 'GME', 'BUY', 'Market'))
        conn.commit()
    except Exception as e:
        pass
    finally:
        conn.close()
    
    res_b = client.get('/api/trading/trades', headers={'Cookie': f"session_token={users['B']['token']}"})
    assert oid not in str(res_b.data)
