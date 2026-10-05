import os
import sys
import json
import uuid
import datetime
import subprocess
try:
    import requests
except ImportError:
    import urllib.request as requests_mock
    class DummyResp:
        def __init__(self, data, status):
            self.json_data = data
            self.status_code = status
        def json(self): return self.json_data
    # Fallback to urllib if requests not available for simple gets
    pass

import db

def run_verification() -> dict:
    results = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "verification_id": f"VER-{uuid.uuid4().hex[:8].upper()}",
        "features": [],
        "overall_status": "OPERATIONAL", 
        "counts": {"VERIFIED": 0, "PARTIAL": 0, "FAILED": 0, "NOT VERIFIED": 0}
    }

    # 1. Deployment / Git
    try:
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        env = "RENDER" if "RENDER" in os.environ else "LOCAL"
        
        results["environment"] = {
            "git_sha": sha,
            "deployment": env,
            "render_service": os.environ.get("RENDER_SERVICE_ID", "unknown"),
        }
    except:
        results["environment"] = {"git_sha": "unknown", "deployment": "unknown"}

    # Evaluate Feature: Database
    db_feature = {
        "name": "Database Persistence",
        "category": "Infrastructure",
        "evidence": {},
        "status": "NOT VERIFIED"
    }
    try:
        # Check if actual tables exist and have rows
        is_pg = db.IS_POSTGRES
        db_feature["evidence"]["engine"] = "PostgreSQL" if is_pg else "SQLite"
        conn = db.get_connection()
        cursor = conn.cursor()
        if is_pg:
            cursor.execute("SELECT count(*) FROM users")
        else:
            cursor.execute("SELECT count(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        db_feature["evidence"]["users_count"] = users_count
        db_feature["evidence"]["persistence"] = "VERIFIED (Data found)" if users_count > 0 else "PARTIAL (Tables reachable but empty)"
        db_feature["status"] = "VERIFIED" if is_pg else "PARTIAL" # prefer PG for production
        if not is_pg and users_count > 0:
            db_feature["status"] = "VERIFIED" # If local sqlite but has data, we can call it verified
    except Exception as e:
        db_feature["status"] = "FAILED"
        db_feature["evidence"]["error"] = str(e)
    finally:
        if 'conn' in locals():
            conn.close()
    
    results["features"].append(db_feature)

    # Evaluate Feature: KRONOS Forecast Engine
    forecast_feature = {
        "name": "KRONOS Forecast Engine",
        "category": "Core",
        "evidence": {},
        "status": "NOT VERIFIED"
    }
    
    # We can inspect the local Predictor instance via a global if accessible, but here we run self-tests
    # let's write the file and return so we can flesh it out in webui/app.py context
    
    return results

if __name__ == "__main__":
    print(json.dumps(run_verification(), indent=2))
