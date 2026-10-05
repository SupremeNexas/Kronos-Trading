from webui.strategies.early_signal_scanner import EarlySignalScanner
import json

scanner = EarlySignalScanner()
# Scan ethereum and solana
res = scanner.scan_assets(["ethereum", "solana"])
print(json.dumps(res, indent=2))
