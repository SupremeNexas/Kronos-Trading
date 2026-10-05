import urllib.request
import json
import statistics
import time
import uuid
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from webui.db import get_db_connection, _adapt_query
except ImportError:
    # Fallback for testing standalone
    get_db_connection = None
    _adapt_query = lambda q: q

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

class EarlySignalScanner:
    def __init__(self):
        self.api_key = os.environ.get("COINGECKO_API_KEY", "")
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        if self.api_key:
            self.headers["x-cg-demo-api-key"] = self.api_key
        
        self.volume_ratio_min = 1.5
        self.manual_mentions_min = 3
        self.attention_min_score = 1
        self.momentum_7d_min = 5.0
        self.points_to_flag = 3
        
        # Ensure tables
        if get_db_connection:
            try:
                from webui.db import DatabaseManager
                DatabaseManager.init_db()
            except Exception:
                pass

    def _fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
        except Exception as e:
            pass
        return None

    def _get_historical_volume(self, coin_id: str):
        data = self._fetch_json(f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily")
        if data and "total_volumes" in data:
            volumes = [v[1] for v in data["total_volumes"]]
            if len(volumes) >= 2:
                historical_vols = volumes[:-1]
                if historical_vols:
                    return statistics.median(historical_vols)
        return "UNKNOWN"

    def _get_trending_coins(self):
        data = self._fetch_json(f"{COINGECKO_BASE_URL}/search/trending")
        if data and "coins" in data:
            return [item["item"]["id"] for item in data["coins"]]
        return "UNKNOWN"

    def scan_assets(self, coin_ids: List[str], manual_mentions: Dict[str, int] = None, user_id: str = None) -> List[Dict[str, Any]]:
        if not self.api_key and os.environ.get("FLASK_ENV") != "development":
            # According to requirement, if production key is missing return clear error
            # We'll return an error object inside the array or raise Exception.
            # "return a clear data-source error rather than silently making an unauthenticated request."
            # We will generate a clear error result.
            err = [{
                "strategy_version": "1.0",
                "data_source": "CoinGecko V3 API",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "asset": "ALL",
                "signal_scan_id": str(uuid.uuid4()),
                "volume_ratio": "UNKNOWN",
                "attention_score": "UNKNOWN",
                "momentum_7d": "UNKNOWN",
                "score": 0,
                "decision": "ERROR",
                "reasons": ["COINGECKO_API_KEY is missing. Production environment requires authenticated API access."]
            }]
            return err

        if not manual_mentions:
            manual_mentions = {}
            
        trending_coins = self._get_trending_coins()
        
        results = []
        for coin_id in coin_ids:
            result = self._scan_single_asset(coin_id, trending_coins, manual_mentions.get(coin_id, 0))
            results.append(result)
            
        self._save_scan_history(results, user_id)
        self._update_watchlist(results, user_id)
        
        return results

    def _scan_single_asset(self, coin_id: str, trending_coins, mentions: int) -> Dict[str, Any]:
        result = {
            "strategy_version": "1.0",
            "data_source": "CoinGecko V3 API",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "asset": coin_id,
            "signal_scan_id": str(uuid.uuid4()),
            "volume_ratio": "UNKNOWN",
            "attention_score": "UNKNOWN",
            "momentum_7d": "UNKNOWN",
            "score": 0,
            "decision": "MONITOR",
            "reasons": []
        }

        try:
            url = f"{COINGECKO_BASE_URL}/coins/markets?vs_currency=usd&ids={coin_id}&price_change_percentage=7d"
            data_list = self._fetch_json(url)
            
            if data_list and isinstance(data_list, list) and len(data_list) > 0:
                market_data = data_list[0]
                
                # MOMENTUM
                momentum = market_data.get("price_change_percentage_7d_in_currency")
                if momentum is not None:
                    result["momentum_7d"] = momentum
                    if momentum >= self.momentum_7d_min:
                        result["score"] += 1
                        result["reasons"].append(f"Momentum {momentum:.2f}% >= {self.momentum_7d_min}%")
                    else:
                        result["reasons"].append(f"Momentum {momentum:.2f}% < {self.momentum_7d_min}%")
                else:
                    result["momentum_7d"] = "UNKNOWN"
                    result["reasons"].append("Momentum UNKNOWN")

                # VOLUME
                current_vol = market_data.get("total_volume")
                median_vol = self._get_historical_volume(coin_id)
                
                if current_vol is not None and median_vol != "UNKNOWN" and median_vol > 0:
                    vol_ratio = current_vol / median_vol
                    result["volume_ratio"] = vol_ratio
                    if vol_ratio >= self.volume_ratio_min:
                        result["score"] += 1
                        result["reasons"].append(f"Volume Ratio {vol_ratio:.2f} >= {self.volume_ratio_min}")
                    else:
                        result["reasons"].append(f"Volume Ratio {vol_ratio:.2f} < {self.volume_ratio_min}")
                else:
                    result["volume_ratio"] = "UNKNOWN"
                    result["reasons"].append("Volume Ratio UNKNOWN")
            else:
                result["reasons"].append("Market Data UNKNOWN")

            # ATTENTION
            if trending_coins == "UNKNOWN":
                result["attention_score"] = "UNKNOWN"
                result["reasons"].append("Attention Score UNKNOWN (Trending data unavailable)")
            else:
                att_score = 0
                is_trending = coin_id in trending_coins
                if is_trending:
                    att_score += 1
                if mentions >= self.manual_mentions_min:
                    att_score += 1
                    
                result["attention_score"] = att_score
                if att_score >= self.attention_min_score:
                    result["score"] += 1
                    result["reasons"].append(f"Attention Score {att_score} >= {self.attention_min_score} (Trending: {is_trending}, Mentions: {mentions})")
                else:
                    result["reasons"].append(f"Attention Score {att_score} < {self.attention_min_score}")

            # FINAL DECISION
            if result["score"] >= self.points_to_flag:
                result["decision"] = "WATCHLIST"

        except Exception as e:
            result["reasons"].append(f"Error fetching data: {str(e)}")

        return result

    def _save_scan_history(self, results: List[Dict[str, Any]], user_id: str = None):
        if not get_db_connection: return
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO scanner_history (user_id, signal_scan_id, strategy_version, data_source, timestamp_at, asset, volume_ratio, attention_score, momentum_7d, score, decision, reasons) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        
        for r in results:
            cursor.execute(_adapt_query(sql), (
                user_id, r["signal_scan_id"], r["strategy_version"], r["data_source"], r["timestamp"],
                r["asset"], str(r["volume_ratio"]), str(r["attention_score"]), str(r["momentum_7d"]),
                r["score"], r["decision"], " | ".join(r["reasons"])
            ))
        conn.commit()
        conn.close()

    def _update_watchlist(self, results: List[Dict[str, Any]], user_id=None):
        if not get_db_connection: return
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        
        # INSERT or Update watchlist based on PRIMARY KEY (asset)
        # SQLite: INSERT OR REPLACE
        # PostgreSQL: INSERT ... ON CONFLICT (asset) DO UPDATE ...
        # Handling the generic way is to check existence if we want it cross-DB cleanly.
        # Note: postgres conflict on `asset` requires ON CONFLICT syntax.
        # But we can just use delete & insert easily.
        
        for r in results:
            if r["decision"] == "WATCHLIST":
                cursor.execute(_adapt_query("DELETE FROM scanner_watchlist WHERE asset = ? AND user_id = ?"), (r["asset"], user_id))
                sql = "INSERT INTO scanner_watchlist (user_id, asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(_adapt_query(sql), (
                    user_id, r["asset"], r["signal_scan_id"], r["timestamp"],
                    str(r["volume_ratio"]), str(r["attention_score"]), str(r["momentum_7d"]),
                    r["score"], " | ".join(r["reasons"])
                ))
        conn.commit()
        conn.close()

    def get_scan_history(self, user_id=None) -> List[Dict[str, Any]]:
        if not get_db_connection: return []
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(_adapt_query("SELECT signal_scan_id, timestamp_at, asset, volume_ratio, attention_score, momentum_7d, score, decision, reasons, data_source FROM scanner_history WHERE user_id = ? ORDER BY timestamp_at DESC LIMIT 100"), (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        res = []
        for r in rows:
            res.append({
                "signal_scan_id": r[0], "timestamp": r[1], "asset": r[2],
                "volume_ratio": r[3], "attention_score": r[4], "momentum_7d": r[5],
                "score": r[6], "decision": r[7], "reasons": r[8].split(" | ") if r[8] else [],
                "data_source": r[9]
            })
        # Note: The original returned oldest to newest because we sliced the history array in UI
        # But now we do ORDER BY DESC.
        return res[::-1]

    def get_watchlist(self, user_id=None) -> List[Dict[str, Any]]:
        if not get_db_connection: return []
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(_adapt_query("SELECT asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons FROM scanner_watchlist WHERE user_id = ? ORDER BY timestamp_at DESC"), (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        res = []
        for r in rows:
            res.append({
                "asset": r[0], "signal_scan_id": r[1], "timestamp": r[2],
                "volume_ratio": r[3], "attention_score": r[4], "momentum_7d": r[5],
                "score": r[6], "decision": "WATCHLIST", "reasons": r[7].split(" | ") if r[7] else []
            })
        return res

