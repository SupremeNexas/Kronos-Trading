import os
import sys
import logging
import datetime
from pprint import pprint

sys.path.insert(0, os.path.abspath('.'))

from webui.app import broker, predictor # Ensure to load app context to grab broker/predictor if any
from webui.agents_engine.orchestrator import AgentEngineOrchestrator
from webui.agents_engine.desk_schemas import ForecastDistribution

logging.basicConfig(level=logging.INFO)

def acceptance_test():
    print("====================================")
    print(" AAPL PAPER TRADING LIFECYCLE TEST  ")
    print("====================================")

    # 1. Orchestrator using explicit quantify desks
    # Since we are mocking predictor if None, let's see if we have `predictor` available from app.
    # Notice: loading `app.py` directly might load the large models, that's fine.

    # We will instantiate orchestrator
    print("\n--- STAGE: Initialization ---")
    orchestrator = AgentEngineOrchestrator(broker=broker, predictor=None)
    orchestrator.forecast_desk.forecast = lambda *args, **kwargs: ForecastDistribution(
        symbol="AAPL",
        forecast_model="MOCK_TEST",
        forecast_version="1.0",
        timestamp=datetime.datetime.now(),
        current_price=333.69,
        horizon=14,
        expected_return_pct=0.03,
        median_return_pct=0.03,
        lower_range=320.0,
        upper_range=350.0,
        uncertainty=0.01,
        confidence=0.9,
        directional_prob=0.8,
        source_timestamp=datetime.datetime.now()
    )

    symbol = "AAPL"
    print(f"Targeting symbol: {symbol}")

    # 2. Run Cycle (Research -> Forecast -> Portfolio -> Validation -> Risk -> Confirmation)
    print("\n--- STAGE: Execution Cycle ---")
    result = orchestrator.run_cycle(symbol=symbol, timeframe="1d", pred_len=14, allow_trading=True)

    print("\n--- CYCLE RESULT ---")
    pprint(result)

    if not result.get("success"):
        print("\n[FAIL] Workflow cycle failed.")
        return False

    if result["execution"]["status"] != "PENDING_CONFIRMATION":
        print(f"\n[INFO] Workflow did not reach PENDING_CONFIRMATION. Ended at {result['execution']['status']}.")
        return False

    journal_id = result.get("journal_id")
    print(f"\n[INFO] Generated Journal ID: {journal_id}")

    # 3. Explicit Confirmation (Human Approval)
    print("\n--- STAGE: Explicit Confirmation ---")
    confirm_result = orchestrator.confirm_trade(journal_id, confirm=True)
    print("\n--- CONFIRMATION RESULT ---")
    pprint(confirm_result)

    if not confirm_result.get("success"):
        print("\n[FAIL] Confirmation step failed.")
        return False

    print(f"\n[SUCCESS] Alpaca PAPER Order Result: {confirm_result.get('status')} - ID: {confirm_result.get('order_id')}")

    # 4. Check Traceability / Journal
    print("\n--- STAGE: Journal Entry Audit ---")
    journal = orchestrator.trading_journal._read()
    entry = next((e for e in journal["entries"] if e["id"] == journal_id), None)

    if not entry:
        print("\n[FAIL] Could not find journal entry.")
        return False

    print("\nEvidence from Journal:")
    evidence = {
        "market_timestamp": entry.get("market_data_timestamp"),
        "prediction_decision": entry.get("prediction_decision"),
        "forecast_uncertainty": entry.get("portfolio_target", {}).get("risk_constraints", {}).get("confidence_used", 0) if entry.get("portfolio_target") else "N/A",
        "portfolio_target_weight": entry.get("portfolio_target", {}).get("target_weight", 0) if entry.get("portfolio_target") else "N/A",
        "validation_passed": entry.get("validation_results", {}).get("verdict", "N/A") if entry.get("validation_results") else "N/A",
        "order_state": entry.get("order_id")
    }
    pprint(evidence)

    print("\n====================================")
    print(" ACCEPTANCE TEST SUCCESSFUL ")
    print("====================================")

if __name__ == "__main__":
    acceptance_test()
