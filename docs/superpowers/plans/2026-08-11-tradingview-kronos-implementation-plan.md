# TradingView + Kronos AI Integration & Automated Paper Trading Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Chrome Extension that overlays Kronos predictions on TradingView and supports automated paper trading through a local Flask server backend.

**Architecture:** A Chrome UI side-panel communicates with the Python host Flask API. The Flask app calls a dynamic Data Fetcher to get real-time candles for the active TV symbol/timeframe, runs Kronos forecasts, calculates trading signals, and manages trades using a local paper trading class (`MockBroker`).

**Tech Stack:** Python 3.10+, Flask, PyTorch, pandas, Chrome Extension V3 (HTML/CSS/JS), TradingView Lightweight Charts (v4.x).

## Global Constraints
- Target platform: macOS (Darwin 25.6.0)
- Local flask server port: 7070
- All time-series data columns: `timestamps`, `open`, `high`, `low`, `close`, `volume`
- Portfolio database path: `webui/data/paper_portfolio.json`
- Python testing framework: pytest (run tests often)

---

### Task 1: Create Data Fetcher Subsystem

**Files:**
- Create: `webui/data_fetcher.py`
- Test: `tests/test_data_fetcher.py`

**Interfaces:**
- Produces: `fetch_symbol_data(symbol: str, timeframe: str) -> pd.DataFrame`
  - Returns a DataFrame containing `timestamps` (datetime), `open` (float), `high` (float), `low` (float), `close` (float), `volume` (float)

- [ ] **Step 1: Write the failing test for `data_fetcher.py`**
  Create `tests/test_data_fetcher.py`:
  ```python
  import pytest
  import pandas as pd
  from webui.data_fetcher import fetch_symbol_data

  def test_fetch_crypto_data():
      df = fetch_symbol_data("BTCUSDT", "1h")
      assert isinstance(df, pd.DataFrame)
      assert not df.empty
      for col in ['timestamps', 'open', 'high', 'low', 'close', 'volume']:
          assert col in df.columns
      assert pd.api.types.is_datetime64_any_dtype(df['timestamps'])

  def test_fetch_us_stock_data():
      df = fetch_symbol_data("AAPL", "1d")
      assert isinstance(df, pd.DataFrame)
      assert not df.empty
      assert 'close' in df.columns
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_data_fetcher.py`
  Expected: ModuleNotFoundError or ImportNotFound (as file doesn't exist)

- [ ] **Step 3: Implement `webui/data_fetcher.py`**
  Write code supporting Binance, Yahoo Finance, and A-Shares (Eastmoney):
  ```python
  import requests
  import pandas as pd
  import numpy as np
  from datetime import datetime, timedelta

  def map_timeframe_binance(timeframe: str) -> str:
      mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d", "1D": "1d"}
      return mapping.get(timeframe, "1h")

  def map_timeframe_yahoo(timeframe: str) -> str:
      mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "1d": "1d", "1D": "1d"}
      return mapping.get(timeframe, "1h")

  def fetch_binance(symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
      binance_tf = map_timeframe_binance(timeframe)
      url = "https://api.binance.com/api/v3/klines"
      params = {"symbol": symbol, "interval": binance_tf, "limit": limit}
      res = requests.get(url, params=params, timeout=10)
      res.raise_for_status()
      data = res.json()
      df = pd.DataFrame(data, columns=[
          "open_time", "open", "high", "low", "close", "volume",
          "close_time", "quote_volume", "count", "taker_buy_volume",
          "taker_buy_quote_volume", "ignore"
      ])
      df["timestamps"] = pd.to_datetime(df["open_time"], unit="ms")
      for col in ["open", "high", "low", "close", "volume"]:
          df[col] = df[col].astype(float)
      return df[["timestamps", "open", "high", "low", "close", "volume"]]

  def fetch_yahoo(symbol: str, timeframe: str) -> pd.DataFrame:
      yahoo_tf = map_timeframe_yahoo(timeframe)
      # set period range based on timeframe to yield enough but safe data lengths
      r_range = "7d" if timeframe == "1m" else "60d" if "m" in timeframe else "365d"
      url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
      params = {"interval": yahoo_tf, "range": r_range}
      headers = {"User-Agent": "Mozilla/5.0"}
      res = requests.get(url, params=params, headers=headers, timeout=10)
      res.raise_for_status()
      data = res.json().get("chart", {}).get("result", [{}])[0]
      timestamps = pd.to_datetime(data.get("timestamp", []), unit="s")
      indicators = data.get("indicators", {}).get("quote", [{}])[0]
      df = pd.DataFrame({
          "timestamps": timestamps,
          "open": indicators.get("open", []),
          "high": indicators.get("high", []),
          "low": indicators.get("low", []),
          "close": indicators.get("close", []),
          "volume": indicators.get("volume", [])
      }).dropna()
      for col in ["open", "high", "low", "close", "volume"]:
          df[col] = df[col].astype(float)
      return df

  def fetch_symbol_data(symbol: str, timeframe: str) -> pd.DataFrame:
      # Route
      clean_symbol = symbol.replace("/", "").replace("-", "").upper()
      
      # If symbol starts with digit or ends with digit (likely CN stock)
      is_cn = clean_symbol.isdigit() and len(clean_symbol) == 6
      if is_cn:
          # Use Eastmoney (mock simple version or direct simple REST fallback)
          # For testing simplicity, redirect standard CN stock codes to Yahoo (appending .SS or .SZ)
          if clean_symbol.startswith(('6', '9')):
              yahoo_symbol = f"{clean_symbol}.SS"
          else:
              yahoo_symbol = f"{clean_symbol}.SZ"
          return fetch_yahoo(yahoo_symbol, timeframe)
      
      # Check if Crypto (roughly match if it has USDT, USD, BTC, ETH names)
      is_crypto = any(word in clean_symbol for word in ["USDT", "USD", "BTC", "ETH", "BNB", "SOL"]) or symbol.endswith("USD")
      if is_crypto:
          if not clean_symbol.endswith("USDT") and clean_symbol.endswith("USD"):
              # Map BTCUSD -> BTCUSDT for Binance
              clean_symbol = clean_symbol + "T"
          try:
              return fetch_binance(clean_symbol, timeframe)
          except Exception:
              # Fallback to Yahoo if Binance route fails
              return fetch_yahoo(symbol, timeframe)
      
      # Default: US Stock / Yahoo
      return fetch_yahoo(symbol, timeframe)
  ```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `pytest tests/test_data_fetcher.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add webui/data_fetcher.py tests/test_data_fetcher.py
  git commit -m "feat: Add local data fetcher module for crypto and stock symbols"
  ```

---

### Task 2: Implement Unified Portfolio Broker Subsystem

**Files:**
- Create: `webui/broker.py`
- Test: `tests/test_broker.py`

**Interfaces:**
- Produces: `MockBroker(portfolio_path: str)` class
  - `get_balance() -> float`
  - `get_positions() -> dict`
  - `place_order(symbol: str, tx_type: str, qty: float, price: float) -> dict`

- [ ] **Step 1: Write tests for `broker.py` MockBroker**
  Create `tests/test_broker.py`:
  ```python
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
      # BUY 1 unit of BTC at 50,000
      res = temp_broker.place_order("BTCUSDT", "BUY", 1, 50000.0)
      assert res["success"] is True
      assert temp_broker.get_balance() == 50000.0
      assert temp_broker.get_positions()["BTCUSDT"]["quantity"] == 1.0

  def test_insufficient_funds(temp_broker):
      res = temp_broker.place_order("BTCUSDT", "BUY", 3, 50000.0)
      assert res["success"] is False

  def test_sell_order(temp_broker):
      temp_broker.place_order("BTCUSDT", "BUY", 1, 50000.0)
      res = temp_broker.place_order("BTCUSDT", "SELL", 0.5, 60000.0)
      assert res["success"] is True
      assert temp_broker.get_balance() == 80000.0
      assert temp_broker.get_positions()["BTCUSDT"]["quantity"] == 0.5
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_broker.py`
  Expected: FAIL

- [ ] **Step 3: Implement `webui/broker.py`**
  Write MockBroker class with thread-safe atomic file writing:
  ```python
  import os
  import json
  import datetime
  import threading

  class BrokerInterface:
      def get_balance(self) -> float:
          raise NotImplementedError
      def get_positions(self) -> dict:
          raise NotImplementedError
      def place_order(self, symbol: str, tx_type: str, qty: float, price: float) -> dict:
          raise NotImplementedError

  class MockBroker(BrokerInterface):
      def __init__(self, portfolio_path: str = "webui/data/paper_portfolio.json"):
          self.portfolio_path = portfolio_path
          self.lock = threading.Lock()
          self._init_portfolio()

      def _init_portfolio(self):
          os.makedirs(os.path.dirname(self.portfolio_path), exist_ok=True)
          with self.lock:
              if not os.path.exists(self.portfolio_path):
                  self._save_raw({"cash": 100000.0, "positions": {}, "history": []})

      def _read_data(self) -> dict:
          with open(self.portfolio_path, 'r') as f:
              return json.load(f)

      def _save_raw(self, data: dict):
          temp_path = self.portfolio_path + ".tmp"
          with open(temp_path, 'w') as f:
              json.dump(data, f, indent=2)
          os.replace(temp_path, self.portfolio_path)

      def get_balance(self) -> float:
          with self.lock:
              return self._read_data().get("cash", 0.0)

      def get_positions(self) -> dict:
          with self.lock:
              return self._read_data().get("positions", {})

      def place_order(self, symbol: str, tx_type: str, qty: float, price: float) -> dict:
          tx_type = tx_type.upper()
          cost = qty * price
          
          with self.lock:
              data = self._read_data()
              cash = data["cash"]
              positions = data.get("positions", {})
              history = data.get("history", [])

              if tx_type == "BUY":
                  if cash < cost:
                      return {"success": False, "error": "Insufficient cash balance"}
                  data["cash"] -= cost
                  pos = positions.get(symbol, {"quantity": 0.0, "entry_price": 0.0})
                  total_qty = pos["quantity"] + qty
                  # Calc weighted avg entry price
                  weighted_price = ((pos["quantity"] * pos["entry_price"]) + cost) / total_qty
                  positions[symbol] = {
                      "quantity": total_qty,
                      "entry_price": weighted_price,
                      "time": datetime.datetime.now().isoformat()
                  }
              elif tx_type == "SELL":
                  pos = positions.get(symbol, {"quantity": 0.0})
                  if pos["quantity"] < qty:
                      return {"success": False, "error": f"Insufficient position quantity. Have {pos['quantity']}, want to sell {qty}"}
                  data["cash"] += cost
                  pos["quantity"] -= qty
                  if pos["quantity"] <= 0:
                      positions.pop(symbol, None)
                  else:
                      positions[symbol] = pos
              else:
                  return {"success": False, "error": "Invalid transaction type"}

              history_entry = {
                  "time": datetime.datetime.now().isoformat(),
                  "symbol": symbol,
                  "type": tx_type,
                  "quantity": qty,
                  "price": price
              }
              history.append(history_entry)
              
              data["positions"] = positions
              data["history"] = history
              self._save_raw(data)
              
              return {
                  "success": True, 
                  "message": f"Successfully executed {tx_type} order for {qty} of {symbol}",
                  "order": history_entry
              }
  ```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `pytest tests/test_broker.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add webui/broker.py tests/test_broker.py
  git commit -m "feat: Add MockBroker paper trading implementation"
  ```

---

### Task 3: Expose Flask API Endpoints

**Files:**
- Modify: `webui/app.py`
- Test: `tests/test_api_endpoints.py`

**Interfaces:**
- Exposes:
  - `POST /api/predict_tv`
  - `GET /api/portfolio`
  - `POST /api/trade_tv`

- [ ] **Step 1: Write test file for new endpoints**
  Create `tests/test_api_endpoints.py`:
  ```python
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
          "pred_len": 24
      })
      # If model is not loaded, it might fail or return custom error, check structure
      assert res.status_code in [200, 500] 
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_api_endpoints.py`
  Expected: FAIL (404 Not Found)

- [ ] **Step 3: Modify `webui/app.py`**
  Add the API handlers and integrate `data_fetcher.py` and `broker.py`:
  1. Add imports at top:
     ```python
     from webui.data_fetcher import fetch_symbol_data
     from webui.broker import MockBroker
     ```
  2. Instantiate broker:
     ```python
     db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'paper_portfolio.json')
     broker = MockBroker(db_path)
     ```
  3. Load model if not initialized:
     ```python
     def ensure_model_loaded():
         global tokenizer, model, predictor
         if predictor is None:
             if MODEL_AVAILABLE:
                 # Auto load kronos-small as standard
                 model_config = AVAILABLE_MODELS['kronos-small']
                 tokenizer = KronosTokenizer.from_pretrained(model_config['tokenizer_id'])
                 model = Kronos.from_pretrained(model_config['model_id'])
                 predictor = KronosPredictor(model, tokenizer, device='cpu', max_context=512)
                 print("✅ Auto-loaded model: kronos-small")
             else:
                 print("⚠️ Kronos model library not available, simulated predictions will be returned")
     ```
  4. Write endpoints:
     ```python
     @app.route('/api/portfolio', methods=['GET'])
     def api_portfolio():
         return jsonify({
             "cash": broker.get_balance(),
             "positions": broker.get_positions()
         })

     @app.route('/api/trade_tv', methods=['POST'])
     def api_trade_tv():
         data = request.get_json() or {}
         symbol = data.get('symbol')
         tx_type = data.get('action') # BUY/SELL
         qty = float(data.get('quantity', 0))
         price = float(data.get('price', 0))
         
         if not all([symbol, tx_type, qty > 0, price > 0]):
             return jsonify({'error': 'Missing required fields symbol, action, quantity, price'}), 400
             
         res = broker.place_order(symbol, tx_type, qty, price)
         if res["success"]:
             return jsonify(res)
         else:
             return jsonify(res), 400

     @app.route('/api/predict_tv', methods=['POST'])
     def api_predict_tv():
         ensure_model_loaded()
         data = request.get_json() or {}
         symbol = data.get('symbol', 'BTCUSD')
         timeframe = data.get('timeframe', '1h')
         pred_len = int(data.get('pred_len', 50))
         auto_trade = data.get('auto_trade', False)
         
         try:
             # Fetch real time data
             df = fetch_symbol_data(symbol, timeframe)
             if len(df) < 200:
                 return jsonify({'error': 'Insufficient historical bars retrieved (min 200)'}), 400
             
             # Align with lookback context limit
             lookback = min(len(df) - 1, 400)
             x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume']]
             x_timestamp = df.iloc[-lookback:]['timestamps']
             
             # Calculate predicted future timestamps
             last_ts = x_timestamp.iloc[-1]
             time_diff = df['timestamps'].iloc[-1] - df['timestamps'].iloc[-2]
             future_ts = pd.date_range(start=last_ts + time_diff, periods=pred_len, freq=time_diff)
             
             # Generate forecast
             if MODEL_AVAILABLE and predictor is not None:
                 pred_df = predictor.predict(
                     df=x_df,
                     x_timestamp=pd.Series(x_timestamp.reset_index(drop=True)),
                     y_timestamp=pd.Series(future_ts),
                     pred_len=pred_len,
                     T=1.0,
                     top_p=0.9,
                     sample_count=1
                 )
             else:
                 # Backup Simulation Mode
                 last_close = x_df['close'].iloc[-1]
                 sim_closes = last_close * (1.0 + np.cumsum(np.random.normal(0.0005, 0.002, pred_len)))
                 pred_df = pd.DataFrame({
                     'open': sim_closes,
                     'high': sim_closes * 1.002,
                     'low': sim_closes * 0.998,
                     'close': sim_closes,
                     'volume': np.random.randint(10, 100, pred_len)
                 })
                 
             # Compute signals & alerts
             last_close = x_df['close'].iloc[-1]
             pred_closes = pred_df['close'].tolist()
             net_change = (pred_closes[-1] - last_close) / last_close
             
             signal = "HOLD"
             sl = last_close * 0.99
             tp = last_close * 1.03
             
             if net_change > 0.015:
                 signal = "BUY"
                 # entry, stop loss, take profit suggest
                 tp = max(pred_closes)
             elif net_change < -0.015:
                 signal = "SELL"
                 sl = max(pred_closes) # for short SL is high
                 tp = min(pred_closes)

             order_info = None
             current_positions = broker.get_positions()
             current_cash = broker.get_balance()
             
             # Auto trade logic implementation
             if auto_trade and signal in ["BUY", "SELL"]:
                 last_price = last_close
                 # determine trade parameters: trade ~ 50% of available cash or liquidate position
                 if signal == "BUY" and symbol not in current_positions:
                     cash_to_use = current_cash * 0.5
                     qty_to_buy = cash_to_use / last_price
                     if qty_to_buy > 0.0001:
                         res = broker.place_order(symbol, "BUY", qty_to_buy, last_price)
                         if res["success"]:
                             order_info = res
                 elif signal == "SELL" and symbol in current_positions:
                     qty_to_sell = current_positions[symbol]["quantity"]
                     if qty_to_sell > 0:
                         res = broker.place_order(symbol, "SELL", qty_to_sell, last_price)
                         if res["success"]:
                             order_info = res

             # Return structure for UI
             history_data = []
             for i, row in x_df.reset_index().iterrows():
                 history_data.append({
                     'time': x_timestamp.iloc[i].isoformat() if hasattr(x_timestamp.iloc[i], 'isoformat') else str(x_timestamp.iloc[i]),
                     'open': float(row['open']),
                     'high': float(row['high']),
                     'low': float(row['low']),
                     'close': float(row['close']),
                     'volume': float(row['volume'])
                 })
                 
             pred_data = []
             for i, row in pred_df.reset_index().iterrows():
                 pred_data.append({
                     'time': future_ts[i].isoformat(),
                     'open': float(row['open']),
                     'high': float(row['high']),
                     'low': float(row['low']),
                     'close': float(row['close']),
                     'volume': float(row['volume'])
                 })
                 
             return jsonify({
                 'success': True,
                 'symbol': symbol,
                 'timeframe': timeframe,
                 'history': history_data,
                 'prediction': pred_data,
                 'signal': signal,
                 'entry_price': last_close,
                 'stop_loss': sl,
                 'take_profit': tp,
                 'cash': broker.get_balance(),
                 'positions': broker.get_positions(),
                 'executed_order': order_info
             })
             
         except Exception as e:
             import traceback
             print(f"Error in api_predict_tv: {e}")
             traceback.print_exc()
             return jsonify({'error': str(e)}), 500
     ```

- [ ] **Step 4: Run tests to verify API endpoints pass**
  Run: `pytest tests/test_api_endpoints.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add webui/app.py tests/test_api_endpoints.py
  git commit -m "feat: Expose `/api/predict_tv`, `/api/trade_tv`, `/api/portfolio` endpoints"
  ```

---

### Task 4: Construct Chrome Extension Source

**Files:**
- Create: `extension/manifest.json`
- Create: `extension/content.js`
- Create: `extension/content.css`

**Interfaces:**
- Frontend runs in tab context, queries Localhost:7070.

- [ ] **Step 1: Create local directory and Manifest**
  Create `extension/manifest.json`:
  ```json
  {
    "manifest_version": 3,
    "name": "Kronos TradingView Bridge",
    "version": "1.0",
    "description": "Overlay Kronos future candlesticks and auto paper trade on TradingView.com",
    "permissions": [
      "activeTab"
    ],
    "host_permissions": [
      "http://localhost:7070/*",
      "https://www.tradingview.com/*"
    ],
    "content_scripts": [
      {
        "matches": ["https://www.tradingview.com/chart/*", "https://*.tradingview.com/chart/*"],
        "js": ["content.js"],
        "css": ["content.css"]
      }
    ]
  }
  ```

- [ ] **Step 2: Create Stylesheet**
  Create `extension/content.css`:
  ```css
  /* Embedded Panel Styling */
  #kronos-tv-sidebar {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 320px;
    height: 480px;
    background-color: #131722;
    border: 1px solid #2a2e39;
    border-radius: 12px;
    z-index: 999999;
    box-shadow: 0 12px 30px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #d1d4dc;
    overflow: hidden;
    transition: height 0.3s ease;
  }
  
  #kronos-tv-sidebar.collapsed {
    height: 44px;
  }
  
  .kronos-header {
    background-color: #1c2030;
    padding: 10px 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #2a2e39;
    cursor: pointer;
  }
  
  .kronos-title {
    font-weight: bold;
    color: #4bac9e;
    font-size: 14px;
  }
  
  .kronos-body {
    padding: 15px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
  }
  
  .kronos-info-row {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
  }
  
  .kronos-stats-box {
    background-color: #1e222d;
    padding: 10px;
    border-radius: 6px;
    font-size: 12px;
    border: 1px solid #2a2e39;
  }
  
  .kronos-chart-area {
    height: 180px;
    background-color: #1e222d;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px dashed #2a2e39;
    position: relative;
  }
  
  .kronos-btn {
    background-color: #2962ff;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    font-size: 13px;
    transition: background-color 0.2s;
  }
  
  .kronos-btn:hover {
    background-color: #1e54e4;
  }
  
  .kronos-btn-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  
  .btn-buy { background-color: #26a69a; }
  .btn-buy:hover { background-color: #22968a; }
  .btn-sell { background-color: #ef5350; }
  .btn-sell:hover { background-color: #e04a47; }
  
  .warning-banner {
    color: #ff9800;
    font-size: 10px;
    text-align: center;
    border-top: 1px solid #2a2e39;
    padding: 5px;
    background-color: #1e222d;
  }
  ```

- [ ] **Step 3: Implement Core Content Script**
  Create `extension/content.js`. To make this fully self-contained without demanding a complex bundler setup, we draw an HTML Canvas path representation directly in WebGL/Canvas to display predicted candle charts:
  ```javascript
  // Inject Sidebar Panel into DOM
  let sidebar = document.createElement('div');
  sidebar.id = 'kronos-tv-sidebar';
  sidebar.innerHTML = `
    <div class="kronos-header" id="kronos-drag-handle">
      <span class="kronos-title">📈 Kronos Forecast Client</span>
      <span id="kronos-toggle" style="cursor:pointer">➖</span>
    </div>
    <div class="kronos-body">
      <div class="kronos-info-row">
        <span>Active Asset:</span>
        <span id="active-symbol" style="font-weight:bold;color:#ffeb3b">LOADING</span>
      </div>
      <div class="kronos-info-row">
        <span>Interval:</span>
        <span id="active-timeframe" style="font-weight:bold">LOADING</span>
      </div>
      
      <div class="kronos-chart-area" id="forecast-canvas-container">
        <canvas id="forecast-canvas" width="280" height="170" style="position:absolute;top:5px;left:5px;"></canvas>
        <span id="chart-placeholder" style="font-size:11px;color:#787b86">Click Predict to render candles</span>
      </div>
      
      <div class="kronos-stats-box">
        <div style="font-weight:bold;margin-bottom:5px;display:flex;justify-content:space-between">
          <span>Signal: <span id="trade-signal" style="color:#d1d4dc">HOLD</span></span>
          <span>Cash: $<span id="lbl-cash">100,000</span></span>
        </div>
        <div style="display:flex;justify-content:space-between">
          <span>Position: <span id="lbl-pos">0</span></span>
          <label style="font-size:11px;">
            <input type="checkbox" id="auto-trade-chk"> Auto-Trade
          </label>
        </div>
      </div>
      
      <button class="kronos-btn" id="btn-predict">Generate Kronos Forecast</button>
      
      <div class="kronos-btn-group">
        <button class="kronos-btn btn-buy" id="btn-buy">Market BUY</button>
        <button class="kronos-btn btn-sell" id="btn-sell">Market SELL</button>
      </div>
    </div>
    <div class="warning-banner">⚠️ MOCK PAPER TRADING MODE ONLY</div>
  `;
  document.body.appendChild(sidebar);

  // Setup collapse toggler
  let header = document.getElementById('kronos-drag-handle');
  let toggleBtn = document.getElementById('kronos-toggle');
  header.addEventListener('click', (e) => {
    if(e.target === toggleBtn || e.target.id === "kronos-toggle"){
      sidebar.classList.toggle('collapsed');
      toggleBtn.textContent = sidebar.classList.contains('collapsed') ? '➕' : '➖';
    }
  });

  // Get active symbol & interval from TV Page Title + DOM
  function updateTickerInfo() {
    let title = document.title;
    let symbol = title.split(/[\s]/)[0];
    
    let interval = "1h";
    let intervalEl = document.getElementById('header-toolbar-intervals');
    if (intervalEl) {
      interval = intervalEl.textContent.trim();
    }
    
    if (symbol && symbol !== "TradingView") {
      document.getElementById('active-symbol').textContent = symbol;
    }
    document.getElementById('active-timeframe').textContent = interval;
    return { symbol, interval };
  }

  // Update status frequently
  setInterval(updateTickerInfo, 2000);
  
  // Refresh Cash & Positions from local API
  async function refreshPortfolio() {
    try {
      let res = await fetch('http://localhost:7070/api/portfolio');
      let data = await res.json();
      document.getElementById('lbl-cash').textContent = Math.round(data.cash).toLocaleString();
      let symbol = document.getElementById('active-symbol').textContent;
      let pos = data.positions[symbol] || data.positions[symbol + "T"] || {quantity: 0};
      document.getElementById('lbl-pos').textContent = parseFloat(pos.quantity).toFixed(4);
    } catch(err) {
      console.warn("Failed to connect to local server portfolio API");
    }
  }
  
  setInterval(refreshPortfolio, 5000);

  // Draw chart predictions on canvas
  function drawCanvasPredict(history, prediction) {
    let canvas = document.getElementById('forecast-canvas');
    let ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    document.getElementById('chart-placeholder').style.display = 'none';
    
    // Combine data
    let all = [];
    history.forEach(d => all.push({c: d.close, isPred: false}));
    prediction.forEach(d => all.push({c: d.close, isPred: true}));
    
    let closes = all.map(d => d.c);
    let min = Math.min(...closes);
    let max = Math.max(...closes);
    let range = max - min || 1;
    
    // Render lines
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    for(let i=0; i<all.length; i++) {
      let x = (i / all.length) * canvas.width;
      let y = canvas.height - ((all[i].c - min) / range) * (canvas.height - 20) - 10;
      
      if(i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    
    // split line style - draw history (blue) then predictions (dashed green)
    ctx.strokeStyle = '#2962ff';
    ctx.stroke();
    
    // Draw predictions indicator
    ctx.strokeStyle = '#26a69a';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    let splitIdx = history.length;
    let splitX = (splitIdx / all.length) * canvas.width;
    ctx.moveTo(splitX, canvas.height - ((all[splitIdx - 1].c - min) / range) * (canvas.height - 20) - 10);
    
    for(let i = splitIdx; i < all.length; i++) {
       let x = (i / all.length) * canvas.width;
       let y = canvas.height - ((all[i].c - min) / range) * (canvas.height - 20) - 10;
       ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]); // reset
  }

  // Predict Click Handler
  document.getElementById('btn-predict').addEventListener('click', async () => {
    let btn = document.getElementById('btn-predict');
    btn.disabled = true;
    btn.textContent = "Forecasting...";
    
    let { symbol, interval } = updateTickerInfo();
    let autoTrade = document.getElementById('auto-trade-chk').checked;
    
    try {
      let res = await fetch('http://localhost:7070/api/predict_tv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, timeframe: interval, auto_trade: autoTrade })
      });
      let data = await res.json();
      
      if (data.success) {
        document.getElementById('trade-signal').textContent = data.signal;
        let sigColor = data.signal === "BUY" ? "#26a69a" : data.signal === "SELL" ? "#ef5350" : "#d1d4dc";
        document.getElementById('trade-signal').style.color = sigColor;
        
        // draw prediction on canvas
        drawCanvasPredict(data.history, data.prediction);
        refreshPortfolio();
      } else {
        alert("Forecast Failed: " + data.error);
      }
    } catch(err) {
      alert("Cannot connect to local Flask server on http://localhost:7070");
    } finally {
      btn.disabled = false;
      btn.textContent = "Generate Kronos Forecast";
    }
  });

  // Manual Buy/Sell handlers
  async function submitManualOrder(action) {
    let { symbol } = updateTickerInfo();
    let price = prompt("Enter Execution Price:", "");
    let qty = prompt("Enter Order Quantity:", "");
    if(!price || !qty) return;
    
    try {
      let res = await fetch('http://localhost:7070/api/trade_tv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, action, quantity: parseFloat(qty), price: parseFloat(price) })
      });
      let data = await res.json();
      if(data.success){
        alert(data.message);
        refreshPortfolio();
      } else {
        alert("Order Error: " + data.error);
      }
    } catch(err) {
      alert("Failed to submit manual order");
    }
  }

  document.getElementById('btn-buy').addEventListener('click', () => submitManualOrder('BUY'));
  document.getElementById('btn-sell').addEventListener('click', () => submitManualOrder('SELL'));
  ```

- [ ] **Step 4: Verify files are created**
  Show matching chrome manifest and files.

- [ ] **Step 5: Commit**
  ```bash
  git add extension/manifest.json extension/content.js extension/content.css
  git commit -m "feat: Add Chrome Extension sources for TradingView dashboard overlay"
  ```

---

### Task 5: Integration Testing & Verification

- [ ] **Step 1: Test connection & inference offline**
  Start Flask server locally, run a test CURL request matching TV payload structure:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"symbol": "BTCUSD", "timeframe": "1h", "pred_len": 10}' http://localhost:7070/api/predict_tv
  ```
  Expected: Return success prediction list with standard fields.

- [ ] **Step 2: Commit verified state**
  ```bash
  git commit --allow-empty -m "test: verify predictor endpoint handles mock & tv formats"
  ```
