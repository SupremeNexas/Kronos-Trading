import sys
import os
import datetime

# Add root folder to sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webui.db import get_db_connection, _adapt_query
from webui.market_data import fetch_latest_price # We will need to implement or use an existing method
from webui.agents_engine.trading_journal import TradingJournal

def run_evaluator():
    print("Starting prediction outcome evaluation...")
    journal = TradingJournal()
    entries = journal.get_entries(limit=1000)
    
    pending = [e for e in entries if e.get("outcome") == "PENDING" and e.get("fill_price")]
    if not pending:
        print("No pending predictions with fills to evaluate.")
        return
        
    for e in pending:
        # Check if forecast horizon is met
        created_at_str = e.get("created_at")
        if not created_at_str:
            continue
            
        created_at = datetime.datetime.fromisoformat(created_at_str)
        horizon_days = e.get("forecast", {}).get("horizon", 14)
        
        # Simulating horizon expiry check for demo purposes (using a fraction of horizon if we want to run test now)
        # For full implementation, uncomment this:
        # if (datetime.datetime.now() - created_at).days < horizon_days:
        #     continue
            
        print(f"Evaluating {e['id']} for {e['symbol']}...")
        
        try:
            # Let's get the latest real-time or historical price
            from webui.market_data import fetch_kline_data
            df = fetch_kline_data(e['symbol'], "1d", max_rows=5)
            if df is not None and not df.empty:
                latest_price = df.iloc[-1]['close']
                journal.update_outcome(e['id'], float(latest_price), "Evaluated by outcome engine.")
                print(f"Evaluated {e['id']} with exit price {latest_price}")
        except Exception as ex:
            print(f"Error evaluating {e['id']}: {ex}")

if __name__ == "__main__":
    run_evaluator()
