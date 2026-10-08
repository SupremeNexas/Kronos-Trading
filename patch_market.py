import re

with open('webui/market_data.py', 'r') as f:
    text = f.read()

# Add yfinance fallback to search_symbols
search_old = '''    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        if not self.client:
            return [{"symbol": query, "name": f"Mock {query}", "exchange": "Unknown", "type": "Equity"}]
        try:'''
search_new = '''    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        if not self.client:
            return [{"symbol": query, "name": query.upper(), "exchange": "US", "type": "Equity"}]
        try:'''

# Add yfinance fallback to get_quote
quote_old = '''        if self.client:
            try:
                subclient = getattr(self.client, market_type)
                trade = subclient.get_trade(infoway_sym)

                if trade and len(trade) > 0:
                    data_status = "live"
                    row = trade[0]
                    price = float(row.get('p', 0.0))
                    volume = float(row.get('v', 0.0))

                    # We might need kline to get prev close
                    kline_res = subclient.get_kline(codes=infoway_sym, kline_type=8, count=2)
                    if kline_res and len(kline_res) > 0:
                        candles = kline_res[0].get("respList", [])
                        if len(candles) > 0:
                            current_kline = candles[0]
                            prev_close = float(current_kline.get('o', 0.0))
                            if len(candles) > 1:
                                prev_close = float(candles[1].get('c', 0.0))
                            change = price - prev_close
                            if prev_close > 0:
                                change_pct = (change / prev_close) * 100

            except Exception as e:
                logging.error(f"Infoway get_quote error: {e}")

        return {
            "symbol": symbol.upper(),
            "price": price,
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "data_status": data_status
        }'''

quote_new = '''        if self.client:
            try:
                subclient = getattr(self.client, market_type)
                trade = subclient.get_trade(infoway_sym)

                if trade and len(trade) > 0:
                    data_status = "live"
                    row = trade[0]
                    price = float(row.get('p', 0.0))
                    volume = float(row.get('v', 0.0))

                    # We might need kline to get prev close
                    kline_res = subclient.get_kline(codes=infoway_sym, kline_type=8, count=2)
                    if kline_res and len(kline_res) > 0:
                        candles = kline_res[0].get("respList", [])
                        if len(candles) > 0:
                            current_kline = candles[0]
                            prev_close = float(current_kline.get('o', 0.0))
                            if len(candles) > 1:
                                prev_close = float(candles[1].get('c', 0.0))
                            change = price - prev_close
                            if prev_close > 0:
                                change_pct = (change / prev_close) * 100
            except Exception as e:
                logging.error(f"Infoway get_quote error: {e}")
        else:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.history(period="2d")
                if len(info) >= 1:
                    price = float(info['Close'].iloc[-1])
                    volume = float(info['Volume'].iloc[-1])
                    if len(info) >= 2:
                        prev_close = float(info['Close'].iloc[-2])
                        change = price - prev_close
                        change_pct = (change / prev_close) * 100
                    data_status = "live"
            except Exception as e:
                logging.error(f"YFinance error: {e}")

        return {
            "symbol": symbol.upper(),
            "price": price,
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "data_status": data_status
        }'''

# Add yfinance fallback to get_historical_bars
bars_old = '''    def get_historical_bars(self, symbol: str, timeframe: str = "1d", limit: int = 300) -> Dict[str, Any]:
        market_type = self._determine_market_type(symbol)
        infoway_sym = self._get_infoway_symbol(symbol)

        bars = []
        if self.client:
            try:
                subclient = getattr(self.client, market_type)

                # Default daily logic
                k_type = 8  # Daily
                if timeframe == "1h": k_type = 6
                elif timeframe == "1m": k_type = 1

                res = subclient.get_kline(codes=infoway_sym, kline_type=k_type, count=limit)
                if res and len(res) > 0:
                    candles = res[0].get("respList", [])
                    for c in candles:
                        ts = c.get('t', 0)
                        if isinstance(ts, str):
                            try:
                                dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                            except:
                                dt = datetime.datetime.strptime(ts, "%Y-%m-%d")
                        else:
                            dt = datetime.datetime.fromtimestamp(int(ts))

                        bars.append({
                            "time": dt.isoformat(),
                            "open": float(c.get('o', 0.0)),
                            "high": float(c.get('h', 0.0)),
                            "low": float(c.get('l', 0.0)),
                            "close": float(c.get('c', 0.0)),
                            "volume": float(c.get('v', 0.0))
                        })
            except Exception as e:
                logging.error(f"Infoway get_historical_bars error: {e}")

        return {"symbol": symbol, "bars": bars}'''

bars_new = '''    def get_historical_bars(self, symbol: str, timeframe: str = "1d", limit: int = 300) -> Dict[str, Any]:
        market_type = self._determine_market_type(symbol)
        infoway_sym = self._get_infoway_symbol(symbol)

        bars = []
        if self.client:
            try:
                subclient = getattr(self.client, market_type)

                # Default daily logic
                k_type = 8  # Daily
                if timeframe == "1h": k_type = 6
                elif timeframe == "1m": k_type = 1

                res = subclient.get_kline(codes=infoway_sym, kline_type=k_type, count=limit)
                if res and len(res) > 0:
                    candles = res[0].get("respList", [])
                    for c in candles:
                        ts = c.get('t', 0)
                        if isinstance(ts, str):
                            try:
                                dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                            except:
                                dt = datetime.datetime.strptime(ts, "%Y-%m-%d")
                        else:
                            dt = datetime.datetime.fromtimestamp(int(ts))

                        bars.append({
                            "time": dt.isoformat(),
                            "open": float(c.get('o', 0.0)),
                            "high": float(c.get('h', 0.0)),
                            "low": float(c.get('l', 0.0)),
                            "close": float(c.get('c', 0.0)),
                            "volume": float(c.get('v', 0.0))
                        })
            except Exception as e:
                logging.error(f"Infoway get_historical_bars error: {e}")
        else:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                period_map = {"1d": "ytd", "1h": "1mo", "1m": "7d"}
                interval_map = {"1d": "1d", "1h": "1h", "1m": "1m"}
                hist = ticker.history(period="1y", interval=interval_map.get(timeframe, "1d")).tail(limit)
                for date, row in hist.iterrows():
                    bars.append({
                        "time": date.isoformat(),
                        "open": float(row['Open']),
                        "high": float(row['High']),
                        "low": float(row['Low']),
                        "close": float(row['Close']),
                        "volume": float(row['Volume'])
                    })
            except Exception as e:
                logging.error(f"YFinance error: {e}")

        return {"symbol": symbol, "bars": bars}'''


text = text.replace(search_old, search_new)
text = text.replace(quote_old, quote_new)
text = text.replace(bars_old, bars_new)


with open('webui/market_data.py', 'w') as f:
    f.write(text)
print("Market data patched.")
