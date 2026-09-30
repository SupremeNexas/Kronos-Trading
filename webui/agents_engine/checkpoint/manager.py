import sqlite3
import os
import json
import datetime
import logging
from webui.agents_engine.config import CHECKPOINT_DB_PATH

logger = logging.getLogger(__name__)

class CheckpointManager:
    def __init__(self, db_path: str = CHECKPOINT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_checkpoints (
                analysis_id TEXT,
                symbol TEXT,
                stage TEXT,
                status TEXT,
                timestamp TEXT,
                result TEXT,
                error TEXT,
                PRIMARY KEY (analysis_id, stage)
            )
        """)
        conn.commit()
        conn.close()

    def save_checkpoint(self, analysis_id: str, symbol: str, stage: str, status: str, result: dict = None, error: str = None):
        """Save a node run checkpoint to SQLite."""
        timestamp = datetime.datetime.now().isoformat()
        result_str = json.dumps(result) if result else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO agent_checkpoints (analysis_id, symbol, stage, status, timestamp, result, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (analysis_id, symbol, stage, status.upper(), timestamp, result_str, error))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save SQLite checkpoint: {e}")
        finally:
            conn.close()

    def get_checkpoint(self, analysis_id: str, stage: str) -> dict:
        """Retrieve a checkpoint to see if it completed and can be skipped on resume."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        row = None
        try:
            cursor.execute("""
                SELECT status, result, error FROM agent_checkpoints
                WHERE analysis_id = ? AND stage = ?
            """, (analysis_id, stage))
            row = cursor.fetchone()
        except Exception as e:
            logger.error(f"Failed to query SQLite checkpoint: {e}")
        finally:
            conn.close()

        if row:
            status, result_str, error = row
            result = json.loads(result_str) if result_str else {}
            return {
                "status": status,
                "result": result,
                "error": error
            }
        return None

    def clear_checkpoints(self, analysis_id: str):
        """Delete checkpoints for a completed analysis or on reset."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM agent_checkpoints WHERE analysis_id = ?", (analysis_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to clear SQLite checkpoints: {e}")
        finally:
            conn.close()

    def get_all_stages(self, analysis_id: str) -> dict:
        """Retrieve all completed checkpoints for displaying to UI or merging."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        results = {}
        try:
            cursor.execute("""
                SELECT stage, status, result FROM agent_checkpoints
                WHERE analysis_id = ?
            """, (analysis_id,))
            rows = cursor.fetchall()
            for row in rows:
                stage, status, result_str = row
                results[stage] = {
                    "status": status,
                    "result": json.loads(result_str) if result_str else {}
                }
        except Exception as e:
            logger.error(f"Failed to get stages: {e}")
        finally:
            conn.close()
        return results
