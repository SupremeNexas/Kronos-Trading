import urllib.request
import json
import statistics
import time
import uuid
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

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
        
        self.scans_file = os.path.join(DATA_DIR, "scanner_history.json")
        self.watchlist_file = os.path.join(DATA_DIR, "scanner_watchlist.json")
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(self.scans_file):
            with open(self.scans_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.watchlist_file):
            with open(self.watchlist_file, 'w') as f:
                json.dump([], f)

    def _fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
        except Exception as e:
            # print("Fetch err:", e)
            pass
        return None

    def _get_historical_volume(self, coin_id: str) -> Optional[float]:
        data = self._fetch_json(f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily")
        if data and "total_volumes" in data:
            volumes = [v[1] for v in data["total_volumes"]]
            if len(volumes) >= 2:
                # Ignore the very last one as it might be current day partial
                historical_vols = volumes[:-1]
                if historical_vols:
                    return statistics.median(historical_vols)
        return None

    def _get_trending_coins(self) -> List[str]:
        data = self._fetch_json(f"{COINGECKO_BASE_URL}/search/trending")
        if data and "coins" in data:
            return [item["item"]["id"] for item in data["coins"]]
        return []

    def scan_assets(self, coin_ids: List[str], manual_mentions: Dict[str, int] = None) -> List[Dict[str, Any]]:
        if not manual_mentions:
            manual_mentions = {}
            
        trending_coins = self._get_trending_coins()
        
        results = []
        for coin_id in coin_ids:
            result = self._scan_single_asset(coin_id, trending_coins, manual_mentions.get(coin_id, 0))
            results.append(result)
            
        # Save scan history
        self._save_scan_history(results)
        
        # Update watchlist
        self._update_watchlist(results)
        
        return results

    def _scan_single_asset(self, coin_id: str, trending_coins: List[str], mentions: int) -> Dict[str, Any]:
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
            # Get current data & momentum
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
                    result["reasons"].append("Momentum UNKNOWN")

                # VOLUME
                current_vol = market_data.get("total_volume")
                median_vol = self._get_historical_volume(coin_id)
                if current_vol is not None and median_vol is not None and median_vol > 0:
                    vol_ratio = current_vol / median_vol
                    result["volume_ratio"] = vol_ratio
                    if vol_ratio >= self.volume_ratio_min:
                        result["score"] += 1
                        result["reasons"].append(f"Volume Ratio {vol_ratio:.2f} >= {self.volume_ratio_min}")
                    else:
                        result["reasons"].append(f"Volume Ratio {vol_ratio:.2f} < {self.volume_ratio_min}")
                else:
                    result["reasons"].append("Volume Ratio UNKNOWN")
            else:
                result["reasons"].append("Market Data UNKNOWN")
                result["reasons"].append("Volume Ratio UNKNOWN")

            # ATTENTION
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

    def _save_scan_history(self, results: List[Dict[str, Any]]):
        history = self.get_scan_history()
        history.extend(results)
        history = history[-1000:]
        try:
            with open(self.scans_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception:
            pass
            
    def _update_watchlist(self, results: List[Dict[str, Any]]):
        watchlist = self.get_watchlist()
        wl_dict = {item["asset"]: item for item in watchlist}
        
        for res in results:
            if res["decision"] == "WATCHLIST":
                wl_dict[res["asset"]] = res
                
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(list(wl_dict.values()), f, indent=2)
        except Exception:
            pass

    def get_scan_history(self) -> List[Dict[str, Any]]:
        try:
            with open(self.scans_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def get_watchlist(self) -> List[Dict[str, Any]]:
        try:
            with open(self.watchlist_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
            
