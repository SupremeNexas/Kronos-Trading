import pytest
import os
from webui.broker import MockBroker

@pytest.fixture
def temp_broker(tmp_path):
    db_file = tmp_path / "portfolio.json"
    return MockBroker(str(db_file))

def test_initial_state(temp_broker):
    assert temp_broker.get_balance() == 100000.0
    assert temp_broker.get_positions() == {}

def test_buy_order(temp_broker):
    res = temp_broker.place_order("BTCUSDT", "BUY", 1.0, 50000.0)
    assert res["success"] is True
    assert temp_broker.get_balance() == 50000.0
    assert temp_broker.get_positions()["BTCUSDT"]["quantity"] == 1.0

def test_insufficient_funds(temp_broker):
    res = temp_broker.place_order("BTCUSDT", "BUY", 3.0, 50000.0)
    assert res["success"] is False

def test_sell_order(temp_broker):
    temp_broker.place_order("BTCUSDT", "BUY", 1.0, 50000.0)
    res = temp_broker.place_order("BTCUSDT", "SELL", 0.5, 60000.0)
    assert res["success"] is True
    assert temp_broker.get_balance() == 80000.0
    assert temp_broker.get_positions()["BTCUSDT"]["quantity"] == 0.5
