import pytest
import json
from webui.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['status'] == 'healthy'
    assert 'service' in data
    assert 'hardware' in data

def test_get_portfolio_status(client):
    res = client.get('/api/portfolio')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'cash' in data
    assert 'positions' in data

def test_api_predict_tv_crypto(client):
    res = client.post('/api/predict_tv', json={
        "symbol": "BTCUSD",
        "timeframe": "1h",
        "pred_len": 10
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['success'] is True
    assert data['symbol'] == 'BTCUSD'
    assert 'history' in data
    assert 'prediction' in data
    assert len(data['prediction']) == 10

def test_market_overview(client):
    res = client.get('/api/market/overview')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'indices' in data
    assert 'macro' in data
    assert 'sectors' in data
    assert len(data['indices']) > 0

def test_market_trending(client):
    res = client.get('/api/market/trending')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'gainers' in data
    assert 'losers' in data
    assert 'most_active' in data

def test_news_feed(client):
    res = client.get('/api/news/feed')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['success'] is True
    assert len(data['news']) > 0

def test_forecast_api(client):
    res = client.post('/api/forecast', json={
        "symbol": "AAPL",
        "interval": "1d",
        "horizon": 14
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['symbol'] == 'AAPL'
    assert 'expected_return_pct' in data
    assert 'confidence_pct' in data
    assert 'direction' in data

def test_backtest_api(client):
    res = client.post('/api/backtest', json={
        "symbol": "AAPL",
        "timeframe": "1d",
        "horizon": 10
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['success'] is True
    assert 'backtest' in data
    assert 'mae_pct' in data['backtest']
    assert 'directional_accuracy_pct' in data['backtest']

def test_auth_demo_and_watchlist(client):
    # Test demo login
    res = client.post('/api/auth/demo')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['success'] is True
    user_id = data['user']['id']

    # Test get watchlist
    res = client.get(f'/api/watchlist?user_id={user_id}')
    assert res.status_code == 200
    wl_data = json.loads(res.data)
    assert wl_data['success'] is True

    # Test add item to watchlist
    res = client.post('/api/watchlist', json={
        "user_id": user_id,
        "symbol": "TSLA",
        "name": "Tesla Inc."
    })
    assert res.status_code == 200

    # Test remove item from watchlist
    res = client.delete('/api/watchlist', json={
        "user_id": user_id,
        "symbol": "TSLA"
    })
    assert res.status_code == 200

def test_alerts_lifecycle(client):
    user_id = "user_demo_001"
    # Create alert
    res = client.post('/api/alerts', json={
        "user_id": user_id,
        "symbol": "MSFT",
        "alert_type": "PRICE_ABOVE",
        "target_price": 450.0,
        "condition": "Target reached"
    })
    assert res.status_code == 200
    alert_id = json.loads(res.data)['alert']['id']

    # Fetch alerts
    res = client.get(f'/api/alerts?user_id={user_id}')
    assert res.status_code == 200

    # Delete alert
    res = client.delete('/api/alerts', json={
        "user_id": user_id,
        "alert_id": alert_id
    })
    assert res.status_code == 200
