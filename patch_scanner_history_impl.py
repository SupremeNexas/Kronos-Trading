import re

with open('webui/strategies/early_signal_scanner.py', 'r') as f:
    content = f.read()

content = content.replace(
    'def get_scan_history(self) -> List[Dict[str, Any]]:',
    'def get_scan_history(self, user_id=None) -> List[Dict[str, Any]]:'
)

# Fix sql parameter
content = content.replace(
    'SELECT signal_scan_id, asset, timestamp_at, volume_ratio, attention_score, momentum_7d, score, decision, reasons FROM scanner_history ORDER BY timestamp_at DESC LIMIT 50',
    'SELECT signal_scan_id, asset, timestamp_at, volume_ratio, attention_score, momentum_7d, score, decision, reasons FROM scanner_history WHERE user_id = ? ORDER BY timestamp_at DESC LIMIT 50'
)

content = content.replace(
    'cursor.execute(_adapt_query("SELECT signal_scan_id, asset, timestamp_at, volume_ratio, attention_score, momentum_7d, score, decision, reasons FROM scanner_history WHERE user_id = ? ORDER BY timestamp_at DESC LIMIT 50"))',
    'cursor.execute(_adapt_query("SELECT signal_scan_id, asset, timestamp_at, volume_ratio, attention_score, momentum_7d, score, decision, reasons FROM scanner_history WHERE user_id = ? ORDER BY timestamp_at DESC LIMIT 50"), (user_id,))'
)


with open('webui/strategies/early_signal_scanner.py', 'w') as f:
    f.write(content)
