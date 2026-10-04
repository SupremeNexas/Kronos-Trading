import time
import os
import sys
import datetime
import threading
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

SCHEDULES = [
    {"symbol": "AAPL", "timeframe": "1d", "forecast_horizon": 14, "mode": "PAPER_CONFIRM"},
    {"symbol": "MSFT", "timeframe": "1d", "forecast_horizon": 14, "mode": "PAPER_CONFIRM"}
]

def run_schedule():
    # Only run once a day ideally, for now just poll every hour
    # We will trigger the API /api/agent_run
    print(f"[{datetime.datetime.now()}] running scheduler...")
    
    for s in SCHEDULES:
        print(f"Triggering prediction for {s['symbol']}")
        try:
            # We call the local flask app if running
            response = requests.post(
                "http://localhost:7070/api/agent_run",
                json={
                    "symbol": s["symbol"], 
                    "timeframe": s["timeframe"], 
                    "allow_trading": True,
                    "mode": s["mode"]
                },
                timeout=120
           )
            if response.status_code == 200:
                print(f"Success for {s['symbol']}: {response.json().get('success')}")
        except Exception as e:
            print(f"Failed to run scheduled task for {s['symbol']}: {e}")

def start_scheduler_thread():
    def loop():
        while True:
            # wait 24 hours in reality, here doing 1h
            time.sleep(3600)
            run_schedule()
            
            # also run evaluator
            try:
                import webui.evaluate_outcomes
                webui.evaluate_outcomes.run_evaluator()
            except:
                pass
            
    t = threading.Thread(target=loop, daemon=True)
    t.start()

if __name__ == "__main__":
    run_schedule()
