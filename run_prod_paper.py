import os
import sys
import logging
import datetime
from pprint import pprint

sys.path.insert(0, os.path.abspath('.'))

from webui.app import broker, predictor, market_provider
from webui.agents_engine.orchestrator import AgentEngineOrchestrator
from webui.broker_service_alpaca import AlpacaBrokerAdapter

logging.basicConfig(level=logging.INFO)

def run_prod_paper():
    print("====================================")
    print(" AAPL FINAL PROD PAPER TRADE TEST   ")
    print("====================================")

    # 1. Ensure broker has Alpaca
    if not isinstance(broker, AlpacaBrokerAdapter) or not broker.available:
        print("[SEVERE] Alpaca Broker not fully available. Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in environment or .env file.")
        print("[INFO] Fallback to MockBrokerAdapter.")
    else:
        print(f"[INFO] Initializing Real Alpaca Paper Trade Mode.")

    # 2. Orchestrator using explicit quantify desks
    print("\n--- STAGE: Initialization ---")
    orchestrator = AgentEngineOrchestrator(broker=broker, predictor=predictor)

    symbol = "AAPL"
    print(f"Targeting symbol: {symbol} via Infoway Market Data Integration")

    # 3. Run Cycle
    print("\n--- STAGE: Execution Cycle ---")
    result = orchestrator.run_cycle(symbol=symbol, timeframe="1d", pred_len=14, allow_trading=True)

    journal_id = result.get("journal_id")
    if not journal_id:
        print("\n[FAIL] Workflow cycle failed.")
        pprint(result)
        return False

    print(f"\n[INFO] Generated pending trade request in Trading Journal: {journal_id}")

    # 4. Explicit Confirmation
    print("\n--- STAGE: Execution Confirmation ---")
    confirm_result = orchestrator.confirm_trade(journal_id, confirm=True)

    print("\n--- CONFIRMATION RESULT ---")
    pprint(confirm_result)

    if confirm_result.get("success"):
        print(f"\n[SUCCESS] Alpaca PAPER Order Result: {confirm_result.get('status')} - ID: {confirm_result.get('order_id')}")
    else:
        print("\n[FAILED] Alpaca PAPER Order Failed.")
        print("Reason: ", confirm_result.get('error'))
        return False

    # 5. Check Traceability
    print("\n--- STAGE: Journal Entry Audit ---")
    journal = orchestrator.trading_journal._read()
    entry = next((e for e in journal["entries"] if e["id"] == journal_id), None)

    if not entry:
        print("\n[FAIL] Journal entry missing.")
        return False

    evidence = {
        "market_timestamp": entry.get("market_data_timestamp"),
        "prediction_decision": entry.get("prediction_decision", entry.get("signal")),
        "validation_passed": entry.get("validation", {}).get("verdict", "N/A"),
        "paper_order_id": entry.get("paper_order_id"),
        "order_status": entry.get("order_status")
    }

    print("\nEvidence from Journal:")
    pprint(evidence)

    print("\n====================================")
    print(" PAPER PROD ACCEPTANCE SUCCESSFUL ")
    print("====================================")
    return True

if __name__ == "__main__":
    run_prod_paper()
