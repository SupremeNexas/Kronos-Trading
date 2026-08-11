import pytest
import json
from webui.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

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
