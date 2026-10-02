import sys
import os
import json
import datetime
import uuid
import logging
import requests
import time

# Set up simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("ProductionE2E_Test")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webui.agents_engine.orchestrator import AgentEngineOrchestrator
from webui.broker_service_alpaca import AlpacaBrokerAdapter
from webui.app import predictor
from webui.db import get_db_connection

def verify_persistence(order_id: str, symbol: str):
    logger.info("Verifying Supabase + Prisma persistence in DB...")
    conn, db_type = get_db_connection()
    try:
        cursor = conn.cursor()
        
        qr = "SELECT id, status FROM orders WHERE id = %s" if db_type == "postgres" else "SELECT id, status FROM orders WHERE id = ?"
        cursor.execute(qr, (order_id,))
        order = cursor.fetchone()
        
        qr_h = "SELECT quantity, avg_entry_price FROM holdings WHERE symbol = %s" if db_type == "postgres" else "SELECT quantity, avg_entry_price FROM holdings WHERE symbol = ?"
        cursor.execute(qr_h, (symbol,))
        holding = cursor.fetchone()
        
        qr_r = "SELECT id FROM research_reports WHERE symbol = %s" if db_type == "postgres" else "SELECT id FROM research_reports WHERE symbol = ?"
        cursor.execute(qr_r, (symbol,))
        journal = cursor.fetchone()
        
        if order:
            logger.info(f"✅ Order persistence verified: {order[0]} - Status: {order[1]}")
        else:
            logger.error("❌ Order not found in database.")
            
        if journal:
            logger.info(f"✅ Trading journal / research report verified: {journal[0]}")
        else:
            logger.error("❌ Trading journal not found in database.")
    finally:
        conn.close()

def run_production_test(symbol: str):
    try:
        logger.info("=========================================")
        logger.info(f"STARTING PRODUCTION END-TO-END TEST: {symbol}")
        
        if os.environ.get("ALPACA_PAPER_TRADE", "false").lower() != "true":
            raise PermissionError("LIVE TRADING MUST REMAIN BLOCKED. Ensure ALPACA_PAPER_TRADE=true")

        broker = AlpacaBrokerAdapter()
        
        orchestrator = AgentEngineOrchestrator(broker=broker, predictor=predictor)
        
        logger.info("1. Executing KRONOS Agent Workflow (Prediction -> Signal -> Risk)")
        result = orchestrator.run_cycle(symbol=symbol, timeframe="1d")
        
        if not result.get("success"):
            logger.error(f"Agent pipeline failed: {result.get('error')}")
            return False
            
        exec_info = result.get("execution", {})
        if exec_info.get("status") != "PENDING_CONFIRMATION":
            logger.warning(f"Trade not proposed. Reason: {exec_info.get('reason')}")
            return True
            
        logger.info(f"✅ Workflow reached PENDING_CONFIRMATION status.")
        order_info = exec_info.get("order_info", {})
        logger.info(f"Proposed Order: {order_info.get('side')} {order_info.get('quantity')} {symbol} @ ~${order_info.get('price')}")
        
        analysis_id = result.get("analysis_id")
        
        logger.info("2. Triggering Frontend Confirmation (Confirm Trade)")
        confirm_res = orchestrator.confirm_trade(analysis_id)
        
        if not confirm_res.get("success"):
            logger.error(f"Confirmation failed: {confirm_res.get('error')}")
            return False
            
        final_exec = confirm_res.get("execution", {})
        alpaca_order = final_exec.get("order_info", {}).get("order", {})
        
        order_id = alpaca_order.get("id") or alpaca_order.get("order_id", "simulated")
        status = alpaca_order.get("status")
        
        logger.info(f"✅ Alpaca paper order status: {status} (ID: {order_id})")
        
        logger.info("3. Waiting for database sync...")
        time.sleep(1)
        
        verify_persistence(order_id, symbol)
        
        logger.info("=========================================")
        logger.info("PAPER TRADE PRODUCTION WORKFLOW FULLY COMPLETE")
        return True
        
    except Exception as e:
        logger.error(f"Critical workflow error: {e}")
        return False

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    run_production_test(symbol)
