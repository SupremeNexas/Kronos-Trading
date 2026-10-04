import logging
import json
import os
import datetime
from typing import Dict, Any
from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.INFO)

import sys
from webui.agents_engine.orchestrator import AgentEngineOrchestrator

class MockBroker:
    def get_balance(self):
        return 100000.0
    def get_positions(self):
        return {}
    def submit_order(self, **kwargs):
        class OrderMatch:
            id = "alpaca_paper_test"
        return OrderMatch()

class MockPredictor:
    def predict(self, df):
        import numpy as np
        # Ensure target is significantly higher than support to clear RR ratio
        return np.linspace(df['close'].iloc[-1] * 1.05, df['close'].iloc[-1] * 1.25, 14)

def main():
    print("==================================================")
    print("STARTING ACCEPTANCE TEST")
    print("==================================================")
    
    broker = MockBroker()
    predictor = MockPredictor()
    orchestrator = AgentEngineOrchestrator(broker=broker, predictor=predictor)

    # Patch local method just for testing the successful signal case
    original_calc = orchestrator._calculate_predictions
    def mock_calc(df, symbol, pred_len):
        import numpy as np
        res = original_calc(df, symbol, pred_len)
        last_px = res["last_close"]
        # Boost resistance so R:R >= 2.0 (Risk = 5%, Reward = 10+%)
        res["support"] = last_px * 0.95 
        res["resistance"] = last_px * 1.15
        return res
    orchestrator._calculate_predictions = mock_calc

    # 1. Run cycle for AAPL
    print("\nRunning Production Cycle for AAPL...")
    result = orchestrator.run_cycle(symbol="AAPL", timeframe="1d")
    
    print("\n--- Cycle Result ---")
    print(json.dumps(result, indent=2))
    
    # 2. Confirm if PENDING_CONFIRMATION
    if result.get("execution", {}).get("status") == "PENDING_CONFIRMATION":
        journal_id = result.get("journal_id")
        print(f"\nTrade requires Confirmation! Journal ID: {journal_id}")
        print("Submitting explicit User Confirmation to proceed paper trade...")
        confirm_result = orchestrator.confirm_trade(journal_id, True)
        print("\n--- Confirmation Result ---")
        print(json.dumps(confirm_result, indent=2))
        
        # 3. Print journal contents to verify everything is persisted
        print("\n--- Verifying Journal Persistence ---")
        journal = orchestrator.trading_journal._read()
        target_entry = next((x for x in journal["entries"] if x["id"] == journal_id), None)
        if target_entry:
            print("Journal Entry Found:")
            print(json.dumps(target_entry, indent=2))
            
            # Print specific guide points
            print("\nMethodology check:")
            print("Decision:", target_entry.get("prediction_decision"))
            evidence = target_entry.get("evidence", {})
            print("Supporting Evidence:", evidence.get("supporting_evidence"))
            print("Opposing Evidence:", evidence.get("opposing_evidence"))
            print("Missing Information:", evidence.get("missing_information"))
            print("Validation Check:", target_entry.get("validation", {}).get("verdict"))
            print("Order Status:", target_entry.get("order_status"))
            
        else:
            print("Journal entry missing!")
    else:
        print("\nCycle ended in NO_TRADE or WAIT. This tests failure safely.")

if __name__ == "__main__":
    main()
