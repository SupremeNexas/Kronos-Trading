# Design Specification: TradingView + Kronos AI Integration & Automated Paper Trading Bridge

**Date**: 2026-08-11
**Status**: APPROVED

---

## 1. Architectural Overview

The goal of this feature is to allow users to trade on `tradingview.com` using Kronos's predictive intelligence. The connection consists of three primary components:
1. **Chrome Extension (Frontend)**: Reads the active symbol/timeframe from TradingView, provides a floating dashboard/control widget, and draws forecasts in a companion pane using `TradingView Lightweight Charts`.
2. **Flask API Endpoint `/api/predict_tv`**: Receives requests, fetches live market data dynamically for crypto/global stocks/A-shares, runs the `KronosPredictor` model, and computes trading signals.
3. **Unified Broker Interface (`broker.py`)**: Manages the paper portfolio and live broker integration (mocked now for paper trading; future-ready for Zerodha/Kite Connect).

```
   +-----------------------------------------------------------+
   |                Browser: TradingView.com                  |
   |                                                           |
   |   [ TradingView Chart Canvas ]     [ Floating Widget UI ] |
   |               |                               |           |
   |  (Scraped Ticker & Interval)   (Manual/Auto Trade Orders) |
   +---------------+-------------------------------+-----------+
                   |                               ^
        1. POST /api/predict_tv        3. Order Response / Update
                   v                               |
   +---------------+-------------------------------+-----------+
   |               Flask Server (localhost:7070)               |
   |                                                           |
   |   +-------------------+       +-----------------------+   |
   |   |   kronos.py       |       |   broker.py           |   |
   |   |   (Model inference|       |   (Portfolio Manager)     |   |
   |   |    & Signal Gen)  |       |       +---------------+   |   |
   |   +---------+---------+       |       | MockBroker    |   |   |
   |             | (Candles)       |       | (Local Paper  |   |   |
   |             v                 |       |  Engine)      |   |   |
   |   +---------+---------+       |       +---------------+   |   |
   |   |   Data Fetcher    |       |       | ZerodhaBroker |   |   |
   |   |   (Binance/Yahoo/ |       |       | (Future App)  |   |   |
   |   |    Eastmoney API) |       |       +---------------+   |   |
   |   +-------------------+       +-----------------------+   |
   +-----------------------------------------------------------+
```

---

## 2. Component Design

### A. Chrome Extension (`extension/`)

#### 1. `manifest.json` (V3)
Manages permissions and assets:
- `host_permissions`: Access to `http://localhost:7070/*` and `https://www.tradingview.com/*`.
- `content_scripts`: Registers `content.js` to run on `https://www.tradingview.com/chart/*`.
- `web_accessible_resources`: Local assets like CSS styles and libraries (`lightweight-charts.standalone.production.js`).

#### 2. `content.js` (DOM Scraper and UI Manager)
- **Scraping Info**:
  - Ticker Name: Extracted via `document.title.split(/[\s]/)[0]` which yields the symbol (e.g. `BTCUSD` or `AAPL`).
  - Interval (timeframe): Extracted via `document.getElementById('header-toolbar-intervals').textContent.trim()`.
- **Observer Loop**: Monitors the page `<title>` using `MutationObserver` to detect symbol changes without page reloads (Single Page App behavior).
- **Floating Panel Injection**:
  - Injects a `div` element with a shadow DOM (to prevent TradingView styles from breaking the widget) in the bottom-right corner.
  - Contains:
    - Current Active Symbol & Timeframe badge.
    - Forecast action buttons (`Generate Forecast`, `Toggle Panel`).
    - Mini TradingView Lightweight Chart pane.
    - Current Paper Portfolio status (Cash: ₹XXXX, Active Position: X units).
    - Trade buttons: `BUY`, `SELL`, and `Auto-Trade Toggle`.

---

### B. Flask Server Additions (`webui/`)

#### 1. Endpoint: `POST /api/predict_tv`
Accepts:
```json
{
  "symbol": "BTCUSD",
  "timeframe": "1h",
  "model_key": "kronos-small",
  "pred_len": 50,
  "auto_trade": false
}
```

Steps performed:
1. **Identify Asset Class**: 
   - Cryptocurrencies (ends with `USD`, `USDT`, `BTC`, etc.).
   - US Equities / Indices (alphabetical, 1-4 letters, e.g. `AAPL`, `MSFT`).
   - Chinese Equities (6-digit numeric codes, e.g. `600580`).
2. **Fetch Data**:
   - Gets raw historical candlestick data (min 200, max 512 context length bars).
   - If timeframe conversions are needed (e.g. TradingView "1h" to Binance "1h"), processes the strings.
3. **Run Prediction**:
   - Runs `predictor.predict()` using the selected Kronos model.
4. **Evaluate Signals & Execute Auto-Trade**:
   - Analyzes predicted price trajectory (e.g., if predicted close over next 10 bars increases by > 1.5%, a Buy recommendation is generated).
   - If `auto_trade` is true, triggers an automated order against `MockBroker` if a trade condition is met.
5. **Return Payload**:
   - Time series of historical and predicted candles.
   - Trade signal (`BUY`, `SELL`, `HOLD`) and suggested limits (EP, SL, TP).
   - Up-to-date Broker status.

---

### C. Unified Broker Interface (`webui/broker.py`)

A base class `BrokerInterface` serves as the contract.

```python
import os
import json
import datetime

class BrokerInterface:
    def get_balance(self) -> float:
        raise NotImplementedError
    def get_positions(self) -> list:
        raise NotImplementedError
    def place_order(self, symbol: str, transaction_type: str, quantity: int, price: float, order_type: str = "MARKET") -> dict:
        raise NotImplementedError
```

#### 1. `MockBroker` Implementation Details
- Stored state in `data/paper_portfolio.json`.
  ```json
  {
    "cash": 100000.0,
    "positions": {
      "BTCUSDT": {
        "quantity": 0.5,
        "entry_price": 60500.0,
        "time": "2026-08-11T10:00:00"
      }
    },
    "history": [
      {
        "time": "2026-08-11T10:00:00",
        "symbol": "BTCUSDT",
        "type": "BUY",
        "quantity": 0.5,
        "price": 60500.0
      }
    ]
  }
  ```
- **Order Execution logic**: Validates cash balance for BUYs. Deducts cash, increases positions. For SELLs, verifies current position size and converts holding back to cash.

---

## 3. Data Integration mapping

### Timeframe Mappings:
| TradingView Name | Yahoo Finance Code | Binance API Code | Eastmoney Code |
|------------------|---------------------|-------------------|----------------|
| 1m               | 1m                  | 1m                | 1              |
| 5m               | 5m                  | 5m                | 5              |
| 15m              | 15m                 | 15m               | 15             |
| 1h               | 1h                  | 1h                | 60             |
| 4h               | -                   | 4h                | 240            |
| 1D / D           | 1d                  | 1d                | 101            |

### Symbol Mappings:
- Tickers parsed, e.g. `BTCUSD` or `BTCUSDT` are routed to Binance `BTCUSDT`.
- Equities parsed, e.g. `AAPL` is routed to Yahoo `AAPL`.
- Chinese tickers, e.g. `600580` is routed to Eastmoney.

---

## 4. Safety Constraints & Edge Cases
1. **Model Execution Safety**: Because predictions run on Flask, heavy concurrent network calls could cause bottlenecks. Runs are sequentialised or handled via standard Python threading.
2. **Persistence Integrity**: Writes to `data/paper_portfolio.json` must be atomic (using a tempfile write-and-replace mechanism) to prevent corruption during concurrent requests.
3. **No Real Orders Placed**: A warning header will be persistently visible on the Floating Extension UI: *"MOCK PAPER TRADING MODE ONLY"*.
4. **Timezone Alignment**: High-frequency data timestamps retrieved from outer APIs will be unified to ISO 8601 UTC to ensure perfect continuity between historical and forecasted data on the charts.

---

## Sources
- [TradingView Lightweight Charts API Guide](https://tradingview.github.io/lightweight-charts/docs/api)
- [Binance API Spot endpoint rules](https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data)
- [Yahoo Finance Chart v8 Schema](https://query1.finance.yahoo.com)
