import re

with open('webui/agents_engine/orchestrator.py', 'r') as f:
    content = f.read()

new_confirm = """
    def confirm_trade(self, analysis_id: str) -> Dict[str, Any]:
        \"\"\"
        Executes a PAPER trade after explicit user confirmation.
        \"\"\"
        # Retrieve state from checkpoint
        exec_checkpoint = self.checkpoint_mgr.get_checkpoint(analysis_id, "EXECUTION")
        if not exec_checkpoint or exec_checkpoint.get("status") != "SUCCESS":
            return {"success": False, "error": "No pending execution found or invalid state."}
            
        exec_result = exec_checkpoint["result"]
        if exec_result.get("status") != "PENDING_CONFIRMATION":
            return {"success": False, "error": f"Order is not in pending confirmation state. Current: {exec_result.get('status')}"}
            
        order_info = exec_result.get("order_info")
        if not order_info:
            return {"success": False, "error": "Order details missing in checkpoint."}
            
        symbol = order_info["symbol"]
        action = order_info["side"]
        final_qty = order_info["quantity"]
        price = order_info["price"]
        
        try:
            # Place order on paper account
            order = self.broker.place_order(
                symbol=symbol,
                side=action,
                quantity=final_qty,
                price=price
            )
            
            final_exec = {
                "executed": order.get("success", False),
                "order_info": order,
                "reason": order.get("message", "Order placed successfully")
            }
            
            # STAGE 6: Memorization of Trading Decisions (Trading Journal)
            if final_exec["executed"]:
                # STAGE 2 & 3 checkpoints shouldn't be lost
                forecast = self.checkpoint_mgr.get_checkpoint(analysis_id, "FORECAST")["result"]
                proposal = self.checkpoint_mgr.get_checkpoint(analysis_id, "LLM_ANALYSIS")["result"]
                
                # Retrieve Alpaca order details
                broker_order = order.get("order", {})
                alpaca_order_id = broker_order.get("id", "SIMULATED_ORDER_ID")
                order_status = broker_order.get("status", "accepted")

                self.memory_mgr.store_decision(
                    symbol=symbol,
                    ai_decision=proposal,
                    kronos_direction=forecast.get("signal", "HOLD"),
                    risk_level="MEDIUM",
                    entry_price=price
                )
                
                # --- Supabase + Prisma persistence layer (via db.py) ---
                user_id = "user_demo_001"
                try:
                    from webui.db import DatabaseManager
                    # Persist actual order to database
                    DatabaseManager.record_order(
                        user_id=user_id,
                        symbol=symbol,
                        side=action,
                        qty=final_qty,
                        price=price,
                        status=order_status,
                        order_id=alpaca_order_id
                    )
                    
                    # Also record in journal table if we want a formal research report
                    import json
                    journal_data = json.dumps({
                        "trade": True,
                        "analysis_id": analysis_id,
                        "order_id": alpaca_order_id,
                        "status": order_status,
                        "ai_decision": proposal,
                        "kronos_direction": forecast.get("signal", "HOLD")
                    })
                    
                    from webui.db import get_db_connection, IS_POSTGRES
                    conn, db_type = get_db_connection()
                    try:
                        cursor = conn.cursor()
                        import uuid
                        uid = f"rep_{uuid.uuid4().hex[:10]}"
                        qr = "INSERT INTO research_reports (id, symbol, report_json) VALUES (%s, %s, %s)" if db_type == "postgres" else "INSERT INTO research_reports (id, symbol, report_json) VALUES (?, ?, ?)"
                        cursor.execute(qr, (uid, symbol, journal_data))
                        conn.commit()
                    finally:
                        conn.close()

                except Exception as db_e:
                    logger.error(f"Failed DB Persistence: {db_e}")
                
            # Update checkpoint
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, "EXECUTION", "SUCCESS", result=final_exec)
            self.checkpoint_mgr.clear_checkpoints(analysis_id)
            
            return {"success": True, "execution": final_exec}
        except Exception as e:
            return {"success": False, "error": str(e)}
"""

old_confirm = re.search(r'    def confirm_trade\(self, analysis_id: str\) -> Dict\[str, Any\]:.*?return \{"success": False, "error": str\(e\)\}', content, re.DOTALL)
if old_confirm:
    content = content[:old_confirm.start()] + new_confirm + content[old_confirm.end():]
    with open('webui/agents_engine/orchestrator.py', 'w') as f:
        f.write(content)
    print("Updated confirm_trade.")
else:
    print("Could not match confirm_trade.")
