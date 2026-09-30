import os
import datetime
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from webui.data_fetcher import fetch_symbol_data
from webui.broker import MockBroker

logger = logging.getLogger(__name__)

class ContextBuilder:
    def __init__(self, portfolio_path: str = "webui/data/paper_portfolio.json"):
        self.broker = MockBroker(portfolio_path)

    def build_context(self, symbol: str, timeframe: str = "1d", kronos_forecast: dict = None) -> dict:
        """
        Builds the unified, immutable shared analysis context.
        Ensures all timestamps are captured and calculations are deterministic.
        """
        analysis_timestamp = datetime.datetime.now().isoformat()

        # 1. Fetch market data using default data_fetcher
        df = pd.DataFrame()
        market_data_status = "OK"
        market_data_time = analysis_timestamp

        try:
            df = fetch_symbol_data(symbol, timeframe)
            if not df.empty:
                market_data_time = df["timestamps"].iloc[-1].isoformat() if "timestamps" in df.columns else analysis_timestamp
            else:
                market_data_status = "EMPTY"
        except Exception as e:
            logger.error(f"Error fetching symbol data for context: {e}")
            market_data_status = f"ERROR: {str(e)}"

        # 2. Build market_data list of OHLCV
        ohlcv_list = []
        if not df.empty:
            # Take last 100 historical bars for agent context to keep token sizes nominal
            recent_df = df.tail(100)
            for _, row in recent_df.iterrows():
                ohlcv_list.append({
                    "date": row["timestamps"].isoformat() if hasattr(row["timestamps"], "isoformat") else str(row["timestamps"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]) if "volume" in row else 0.0
                })

        # 3. Deterministic Technical Indicator Calculation
        technical_indicators = self._calculate_indicators(df)

        # 4. Fetch Fundamentals
        fundamentals = self._fetch_fundamentals_yf(symbol)

        # 5. Fetch News
        news_items = self._fetch_news_yf(symbol)

        # 6. Sentiment Context
        sentiment_context = self._calculate_basic_sentiment(news_items)

        # 7. Portfolio Context
        portfolio_info = {
            "cash": self.broker.get_balance(),
            "positions": self.broker.get_positions(),
            "timestamp": analysis_timestamp
        }

        # 8. Compile everything
        last_price = float(df["close"].iloc[-1]) if not df.empty else 0.0

        context = {
            "symbol": symbol,
            "analysis_timestamp": analysis_timestamp,
            "market_data": {
                "status": market_data_status,
                "timestamp": market_data_time,
                "last_price": last_price,
                "ohlcv": ohlcv_list
            },
            "kronos_forecast": kronos_forecast or {
                "status": "DATA_UNAVAILABLE",
                "model": "N/A",
                "predictions": [],
                "last_price": last_price,
                "forecast_high": last_price,
                "forecast_low": last_price,
                "direction": "NEUTRAL",
                "expected_return": 0.0,
                "forecast_timestamp": analysis_timestamp
            },
            "technical_indicators": technical_indicators,
            "fundamentals": fundamentals,
            "news": news_items,
            "sentiment": sentiment_context,
            "portfolio": portfolio_info
        }

        return context

    def _calculate_indicators(self, df: pd.DataFrame) -> dict:
        """Calculate standard technical indicators deterministically."""
        indicators = {
            "status": "DATA_UNAVAILABLE",
            "timestamp": datetime.datetime.now().isoformat(),
            "sma20": None,
            "ema20": None,
            "rsi": None,
            "macd": {"line": None, "signal": None, "histogram": None},
            "atr": None,
            "volatility_percentage": None
        }

        if df is None or len(df) < 30:
            return indicators

        indicators["status"] = "OK"
        try:
            closes = df["close"]

            # Simple & Exponential Moving Averages
            sma_20 = closes.rolling(window=min(20, len(closes))).mean()
            ema_20 = closes.ewm(span=min(20, len(closes)), adjust=False).mean()

            indicators["sma20"] = float(sma_20.iloc[-1])
            indicators["ema20"] = float(ema_20.iloc[-1])

            # Relative Strength Index (RSI - 14)
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10) # Avoid divide by zero
            rsi = 100 - (100 / (1 + rs))
            indicators["rsi"] = float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0

            # MACD (12, 26, 9)
            ema12 = closes.ewm(span=12, adjust=False).mean()
            ema26 = closes.ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line

            indicators["macd"] = {
                "line": float(macd_line.iloc[-1]),
                "signal": float(signal_line.iloc[-1]),
                "histogram": float(histogram.iloc[-1])
            }

            # Volatility (standard deviation of daily/timeframe returns over last 20 frames)
            returns = closes.pct_change().dropna()
            if not returns.empty:
                indicators["volatility_percentage"] = float(returns.tail(20).std() * 100.0)

            # ATR (Average True Range - 14)
            high_low = df["high"] - df["low"]
            high_cp = (df["high"] - closes.shift()).abs()
            low_cp = (df["low"] - closes.shift()).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean()
            indicators["atr"] = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else 0.0

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            indicators["status"] = f"CALCULATION_ERROR: {str(e)}"

        return indicators

    def _fetch_fundamentals_yf(self, symbol: str) -> dict:
        """Fetch fundamentals data from Yahoo Finance. Safe & fail-open."""
        result = {
            "status": "DATA_UNAVAILABLE",
            "timestamp": datetime.datetime.now().isoformat(),
            "pe_ratio": None,
            "earnings_per_share": None,
            "dividend_yield": None,
            "market_cap": None,
            "revenue": None,
            "gross_margin": None,
            "debt_to_equity": None,
            "free_cash_flow": None
        }

        # Normalize cryptocurrency symbols which yfinance has no fundamentals for
        if "USD" in symbol or "USDT" in symbol:
             return result

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if info:
                result["status"] = "OK"
                result["pe_ratio"] = info.get("trailingPE") or info.get("forwardPE")
                result["earnings_per_share"] = info.get("trailingEps")
                result["dividend_yield"] = info.get("dividendYield")
                result["market_cap"] = info.get("marketCap")
                result["revenue"] = info.get("totalRevenue")
                result["gross_margin"] = info.get("grossMargins")
                result["debt_to_equity"] = info.get("debtToEquity")
                result["free_cash_flow"] = info.get("freeCashflow")
        except Exception as e:
            logger.warning(f"Failed to fetch yfinance fundamentals for {symbol}: {e}")
            result["status"] = "DATA_UNAVAILABLE"

        return result

    def _fetch_news_yf(self, symbol: str) -> list:
        """Fetch news from Yahoo Finance. Safe & fail-open."""
        news_list = []
        try:
            ticker = yf.Ticker(symbol)
            yf_news = ticker.news
            if yf_news:
                for item in yf_news[:5]: # Take top 5 news stories to conserve token context
                    news_list.append({
                        "title": item.get("title"),
                        "publisher": item.get("publisher"),
                        "timestamp": datetime.datetime.fromtimestamp(item.get("providerPublishTime")).isoformat() if item.get("providerPublishTime") else None,
                        "link": item.get("link"),
                        "summary": item.get("summary", "")
                    })
        except Exception as e:
            logger.warning(f"Failed to fetch yfinance news for {symbol}: {e}")

        return news_list

    def _calculate_basic_sentiment(self, news_items: list) -> dict:
        """Calculate a basic deterministic news sentiment before sending to LLM."""
        result = {
            "status": "DATA_UNAVAILABLE",
            "score": 0.0,  # Range -1 to +1
            "sentiment_label": "NEUTRAL"
        }

        if not news_items:
            return result

        # Basic keyword matches for sentiment sizing
        pos_keywords = ["bullish", "grow", "gain", "earnings beat", "buy", "upgrade", "rise", "positive", "high", "success", "innovate", "profit"]
        neg_keywords = ["bearish", "decline", "fall", "earnings miss", "sell", "downgrade", "drop", "negative", "low", "loss", "risk", "debt", "litigation"]

        score = 0.0
        result["status"] = "OK"
        for item in news_items:
            text = (item.get("title", "") + " " + item.get("summary", "")).lower()
            pos_matches = sum(1 for kw in pos_keywords if kw in text)
            neg_matches = sum(1 for kw in neg_keywords if kw in text)

            if pos_matches > neg_matches:
                score += 0.2
            elif neg_matches > pos_matches:
                score -= 0.2

        score = max(-1.0, min(1.0, score))
        result["score"] = float(round(score, 2))
        if score > 0.15:
            result["sentiment_label"] = "POSITIVE"
        elif score < -0.15:
            result["sentiment_label"] = "NEGATIVE"
        else:
            result["sentiment_label"] = "NEUTRAL"

        return result
