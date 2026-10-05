with open("webui/verification_routes.py", "r") as f:
    text = f.read()

import re

# We will completely overwrite run_verification to do actual tests
new_imports = """import os
import subprocess
import json
import uuid
import datetime
from flask import Blueprint, jsonify, request
from webui.db import get_db_connection, IS_POSTGRES
from webui.broker_service_alpaca import AlpacaBrokerAdapter, ALPACA_AVAILABLE
import requests
import traceback
"""

text = re.sub(r'import os\n.*?try:\n\s*import requests\nexcept ImportError:\n\s*pass', new_imports, text, flags=re.DOTALL)

# Re-write run_verification
new_run_verification = """@verification_bp.route('/api/verification/run', methods=['POST'])
def run_verification():
    import traceback
    results = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "verification_id": f"VER-{uuid.uuid4().hex[:8].upper()}",
        "features": [],
        "overall_status": "OPERATIONAL",
        "counts": {"VERIFIED": 0, "PARTIAL": 0, "FAILED": 0, "NOT VERIFIED": 0},
        "claims_vs_evidence": []
    }

    try:
        try:
            sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL, cwd=os.path.dirname(os.path.abspath(__file__))).decode('utf-8').strip()
        except:
            sha = "unknown"
        results["environment"] = {
            "git_sha": sha,
            "deployment": "RENDER" if "RENDER" in os.environ else ("VERCEL" if "VERCEL" in os.environ else "LOCAL/PAPER")
        }

        features_to_check = []
        
        # 1. Database
        db_feat = {"name": "Database Persistence", "category": "AB. Database", "evidence": {}, "status": "NOT VERIFIED"}
        try:
            db_feat["evidence"]["type"] = "PostgreSQL" if IS_POSTGRES else "SQLite"
            conn, _ = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM users")
            ucount = cursor.fetchone()[0]
            db_feat["evidence"]["users"] = ucount
            db_feat["status"] = "VERIFIED"
            conn.close()
            results["claims_vs_evidence"].append({"claim": "Database uses true persistence", "evidence": f"{db_feat['evidence']['type']} check passed", "status": "VERIFIED"})
        except Exception as e:
            db_feat["status"] = "FAILED"
            db_feat["evidence"]["error"] = str(e)
            results["claims_vs_evidence"].append({"claim": "Database uses true persistence", "evidence": str(e), "status": "FAILED"})
        features_to_check.append(db_feat)

        # 2. Authenticaton (Simulated end to end or DB internal check)
        auth_feat = {"name": "Authentication", "category": "B. Authentication", "evidence": {}, "status": "NOT VERIFIED"}
        try:
            from webui.db import DatabaseManager
            test_email = f"test_{uuid.uuid4().hex[:8]}@kronos.ai"
            res_reg = DatabaseManager.create_user(test_email, "KronosTest123!", "Test User")
            if res_reg.get("success"):
                res_login = DatabaseManager.authenticate_user(test_email, "KronosTest123!")
                if res_login.get("success"):
                    auth_feat["status"] = "VERIFIED"
                    auth_feat["evidence"]["result"] = "Register & Login success"
                else:
                    auth_feat["status"] = "FAILED"
            else:
                 auth_feat["status"] = "FAILED"
        except Exception as e:
            auth_feat["status"] = "FAILED"
        features_to_check.append(auth_feat)

        # 3. KRONOS 
        kronos_feat = {"name": "KRONOS Forecast Engine", "category": "E. KRONOS Forecast Engine", "evidence": {}, "status": "NOT VERIFIED"}
        try:
            from webui.forecast_engine import EnsembleForecastEngine
            engine = EnsembleForecastEngine()
            res = engine.generate_forecast("BTCUSD", "1d", 2)
            if "error" not in res and len(res.get("forecast", [])) > 0:
                kronos_feat["status"] = "VERIFIED"
                kronos_feat["evidence"]["sample_target"] = res["forecast"][0].get("close", 0)
            else:
                kronos_feat["status"] = "FAILED"
        except Exception as e:
            kronos_feat["status"] = "FAILED"
            kronos_feat["evidence"]["error"] = str(e)
        features_to_check.append(kronos_feat)

        # 4. Scanner
        scanner_feat = {"name": "Early Signal Scanner", "category": "G. Early Signal Scanner", "evidence": {}, "status": "NOT VERIFIED"}
        try:
            from webui.strategies.early_signal_scanner import EarlySignalScanner
            scanner = EarlySignalScanner()
            if scanner.api_key:
                res = scanner.scan_assets(["bitcoin"])
                if len(res)>0 and res[0]["decision"] != "ERROR":
                    scanner_feat["status"] = "VERIFIED"
                    scanner_feat["evidence"]["bitcoin_decision"] = res[0]["decision"]
                else:
                    scanner_feat["status"] = "FAILED"
            else:
                scanner_feat["status"] = "FAILED"
                scanner_feat["evidence"]["error"] = "No API Key"
        except Exception as e:
            scanner_feat["status"] = "FAILED"
        features_to_check.append(scanner_feat)

        # 5. Alpaca PAPER Integration
        alpaca_feat = {"name": "Alpaca PAPER Integration", "category": "J. Alpaca PAPER Integration", "evidence": {}, "status": "NOT VERIFIED"}
        try:
            if ALPACA_AVAILABLE and (os.environ.get("ALPACA_API_KEY") or os.environ.get("APCA_API_KEY_ID")):
                b = AlpacaBrokerAdapter()
                b.get_account() # throws if invalid
                alpaca_feat["status"] = "VERIFIED"
                alpaca_feat["evidence"]["configuration"] = "Connected to Alpaca Paper"
            else:
                alpaca_feat["status"] = "FAILED"
                alpaca_feat["evidence"]["configuration"] = "No Keys"
        except Exception as e:
            alpaca_feat["status"] = "FAILED"
            alpaca_feat["evidence"]["error"] = str(e)
        features_to_check.append(alpaca_feat)
        
        # 6. Trace verification
        trace_feat = {"name": "Full Scanner->Terminal Trace", "category": "6. Scanner->Terminal Trace", "evidence": {}, "status": "NOT VERIFIED"}
        try:
            conn, _ = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM scanner_trades WHERE alpaca_order_id IS NOT NULL AND alpaca_order_id != ''")
            if cursor.fetchone()[0] > 0:
                trace_feat["status"] = "VERIFIED"
                trace_feat["evidence"]["trace"] = "Real scanner_trade with alpaca UUID found"
            else:
                trace_feat["status"] = "FAILED"
            conn.close()
        except:
             trace_feat["status"] = "FAILED"
        features_to_check.append(trace_feat)

        # Append to results
        critical_unverified = False
        for f in features_to_check:
            results["features"].append(f)
            results["counts"][f["status"]] += 1
            if f["status"] != "VERIFIED":
                critical_unverified = True
            
        if critical_unverified:
            results["overall_status"] = "NON-OPERATIONAL / UNVERIFIED"
        else:
            results["overall_status"] = "OPERATIONAL"
            
    except Exception as e:
        results["overall_status"] = "FAILED"
        results["error"] = str(e)
        results["traceback"] = traceback.format_exc()

    # Save to history
    history = load_history()
    history.insert(0, results)
    save_history(history[:20])

    return jsonify(results)
"""

text = re.sub(r'@verification_bp\.route\(\'/api/verification/run\', methods=\[\'POST\'\]\)\ndef run_verification\(\):.*?(?=\n\n# Save to history)', new_run_verification, text, flags=re.DOTALL)
text = text.replace("# Save to history\n    history = load_history()\n    history.insert(0, results)\n    # Keep only last 20\n    save_history(history[:20])\n\n    return jsonify(results)", "")

with open("webui/verification_routes.py", "w") as f:
    f.write(text)
