with open("webui/strategies/early_signal_scanner.py", "r") as f:
    text = f.read()

# Fix scan_assets missing user_id propagation
text = text.replace("self._save_scan_history(results)", "self._save_scan_history(results, user_id)")
text = text.replace("self._update_watchlist(results)", "self._update_watchlist(results, user_id)")

# Fix save_scan_history doing insert without user_id
old_sql_save = """cursor.execute(_adapt_query(sql), (
                r["signal_scan_id"], r["strategy_version"], r["data_source"], r["timestamp"],
                r["asset"], str(r["volume_ratio"]), str(r["attention_score"]), str(r["momentum_7d"]),
                r["score"], r["decision"], " | ".join(r["reasons"])
            ))"""
new_sql_save = """cursor.execute(_adapt_query(sql), (
                user_id, r["signal_scan_id"], r["strategy_version"], r["data_source"], r["timestamp"],
                r["asset"], str(r["volume_ratio"]), str(r["attention_score"]), str(r["momentum_7d"]),
                r["score"], r["decision"], " | ".join(r["reasons"])
            ))"""
text = text.replace(old_sql_save, new_sql_save)

# Fix update_watchlist doing INSERT without user_id
old_sql_update = """cursor.execute(_adapt_query("DELETE FROM scanner_watchlist WHERE asset = ?"), (r["asset"],))
                sql = "INSERT INTO scanner_watchlist (user_id, asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(_adapt_query(sql), (
                    r["asset"], r["signal_scan_id"], r["timestamp"],
                    str(r["volume_ratio"]), str(r["attention_score"]), str(r["momentum_7d"]),
                    r["score"], " | ".join(r["reasons"])
                ))"""
new_sql_update = """cursor.execute(_adapt_query("DELETE FROM scanner_watchlist WHERE asset = ? AND user_id = ?"), (r["asset"], user_id))
                sql = "INSERT INTO scanner_watchlist (user_id, asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(_adapt_query(sql), (
                    user_id, r["asset"], r["signal_scan_id"], r["timestamp"],
                    str(r["volume_ratio"]), str(r["attention_score"]), str(r["momentum_7d"]),
                    r["score"], " | ".join(r["reasons"])
                ))"""
text = text.replace(old_sql_update, new_sql_update)

# Fix get_scan_history lacking user_id filter
old_get_hist = 'cursor.execute(_adapt_query("SELECT signal_scan_id, timestamp_at, asset, volume_ratio, attention_score, momentum_7d, score, decision, reasons, data_source FROM scanner_history ORDER BY timestamp_at DESC LIMIT 100"))'
new_get_hist = 'cursor.execute(_adapt_query("SELECT signal_scan_id, timestamp_at, asset, volume_ratio, attention_score, momentum_7d, score, decision, reasons, data_source FROM scanner_history WHERE user_id = ? ORDER BY timestamp_at DESC LIMIT 100"), (user_id,))'
text = text.replace(old_get_hist, new_get_hist)

with open("webui/strategies/early_signal_scanner.py", "w") as f:
    f.write(text)
