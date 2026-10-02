import re

with open('webui/agents_engine/orchestrator.py', 'r') as f:
    content = f.read()

# Replace STAGE 5
new_stage_5 = """        # STAGE 5: Order Execution (Actionable Node)
        stage = "EXECUTION"
        checkpoint = self.checkpoint_mgr.get_checkpoint(analysis_id, stage)
        if checkpoint and checkpoint.get("status") == "SUCCESS":
            logger.info("Resuming stage EXECUTION from cache checkpoint.")
            exec_result = checkpoint["result"]
        else:
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "RUNNING")
            try:
                exec_result = {"executed": False, "order_info": None, "reason": "Execution skipped / disallowed"}

                approved = flow_data["validation"].get("approved", False)
                final_qty = flow_data["validation"].get("adjusted_quantity", 0.0)
                action = flow_data["proposal"].get("action", "HOLD")
                
                # Check for NO_TRADE or missing valid requirements
                if action in ["HOLD", "NO_TRADE"] or not approved or final_qty <= 0.0:
                    exec_result["reason"] = f"Execution blocked. Gate Approved: {approved}, Action: {action}, Adjusted Qty: {final_qty}"
                    self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=exec_result)
                else:
                    # Risk is approved. We return a PENDING_CONFIRMATION state instead of auto-submitting.
                    exec_result = {
                        "executed": False,
                        "status": "PENDING_CONFIRMATION",
                        "order_info": {
                            "symbol": symbol,
                            "side": action,
                            "quantity": final_qty,
                            "price": flow_data["current_price"]
                        },
                        "reason": "Requires explicit user confirmation for PAPER TRADE."
                    }
                    self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "SUCCESS", result=exec_result)
            except Exception as e:
                self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, stage, "FAILED", error=str(e))
                return {"success": False, "analysis_id": analysis_id, "stage": stage, "error": str(e)}

        flow_data["execution"] = exec_result

        # Do NOT clear checkpoint history yet, as we need it for confirmation
        # self.checkpoint_mgr.clear_checkpoints(analysis_id)

        return {
            "success": True,
            "analysis_id": analysis_id,
            "current_price": flow_data["current_price"],
            "forecast": flow_data["forecast"],
            "proposal": flow_data["proposal"],
            "validation": flow_data["validation"],
            "execution": flow_data["execution"]
        }

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

                self.memory_mgr.store_decision(
                    symbol=symbol,
                    ai_decision=proposal,
                    kronos_direction=forecast.get("signal", "HOLD"),
                    risk_level="MEDIUM",
                    entry_price=price
                )
            
            # Update checkpoint
            self.checkpoint_mgr.save_checkpoint(analysis_id, symbol, "EXECUTION", "SUCCESS", result=final_exec)
            self.checkpoint_mgr.clear_checkpoints(analysis_id)
            
            return {"success": True, "execution": final_exec}
        except Exception as e:
            return {"success": False, "error": str(e)}"""

import re
old_stage_5 = re.search(r'# STAGE 5: Order Execution.*?flow_data\["execution"\] = exec_result.*?return \{(.*?)\}', content, re.DOTALL)

if old_stage_5:
    content = content[:old_stage_5.start()] + new_stage_5 + content[old_stage_5.end():]
    with open('webui/agents_engine/orchestrator.py', 'w') as f:
        f.write(content)
    print("Orchestrator updated.")
else:
    print("Failed to match STAGE 5.")
