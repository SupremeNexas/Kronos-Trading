import re

with open('webui/db.py', 'r') as f:
    content = f.read()

history_code = """
    @classmethod
    def get_forecast_history(cls, user_id: str) -> List[Dict[str, Any]]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query(\"\"\"
                SELECT p.id, p.symbol, p.model_version, p.forecast_direction, p.predicted_target, 
                       p.confidence, p.data_timestamp, p.timestamp, o.outcome_type, p.created_at
                FROM prediction_runs p
                LEFT JOIN prediction_outcomes o ON p.id = o.prediction_id
                WHERE p.user_id = ?
                ORDER BY p.timestamp DESC, p.created_at DESC
                LIMIT 100
            \"\"\"), (user_id,))
            
            res = []
            for row in cursor.fetchall():
                pid, sym, mv, d, tgt, conf, dts, inf_ts, outc, ca = row
                res.append({
                    "forecast_id": pid,
                    "symbol": sym,
                    "model_version": mv,
                    "direction": d,
                    "target": tgt,
                    "confidence": conf,
                    "data_timestamp": str(dts) if dts else None,
                    "inference_timestamp": str(inf_ts) if inf_ts else None,
                    "outcome": outc,
                    "created_at": str(ca) if ca else None
                })
            return res
        except Exception as e:
            # Fallback for old schema where created_at might be missing
            try:
                cursor.execute(_adapt_query(\"\"\"
                    SELECT p.id, p.symbol, p.model_version, p.forecast_direction, p.predicted_target, 
                           p.confidence, p.data_timestamp, p.timestamp, o.outcome_type
                    FROM prediction_runs p
                    LEFT JOIN prediction_outcomes o ON p.id = o.prediction_id
                    WHERE p.user_id = ?
                    ORDER BY p.timestamp DESC
                    LIMIT 100
                \"\"\"), (user_id,))
                res = []
                for row in cursor.fetchall():
                    pid, sym, mv, d, tgt, conf, dts, inf_ts, outc = row
                    res.append({
                        "forecast_id": pid,
                        "symbol": sym,
                        "model_version": mv,
                        "direction": d,
                        "target": tgt,
                        "confidence": conf,
                        "data_timestamp": str(dts) if dts else None,
                        "inference_timestamp": str(inf_ts) if inf_ts else None,
                        "outcome": outc,
                        "created_at": str(inf_ts) if inf_ts else None
                    })
                return res
            except Exception as e2:
                print("History error:", e2)
                return []
        finally:
            conn.close()
"""
if "def get_forecast_history" not in content:
    content = content.replace("    # Watchlist Operations", history_code + "\n\n    # Watchlist Operations")

with open('webui/db.py', 'w') as f:
    f.write(content)
