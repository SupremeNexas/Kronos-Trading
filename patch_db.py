import re

with open('webui/db.py', 'r') as f:
    content = f.read()

db_methods = """
    @classmethod
    def update_holding(cls, user_id: str, symbol: str, quantity: float, price: float, side: str) -> bool:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(cls._adapt_query_static("SELECT id FROM portfolios WHERE user_id = ? LIMIT 1"), (user_id,))
            pf = cursor.fetchone()
            if not pf:
                return False
            pf_id = pf[0]

            cursor.execute(cls._adapt_query_static("SELECT quantity, avg_entry_price FROM holdings WHERE portfolio_id = ? AND symbol = ?"), (pf_id, symbol))
            holding = cursor.fetchone()

            if holding:
                current_qty, avg_price = holding[0], holding[1]
                if side.upper() == 'BUY':
                    new_qty = current_qty + quantity
                    new_avg = ((current_qty * avg_price) + (quantity * price)) / new_qty
                    cursor.execute(cls._adapt_query_static("UPDATE holdings SET quantity = ?, avg_entry_price = ?, updated_at = CURRENT_TIMESTAMP WHERE portfolio_id = ? AND symbol = ?"), (new_qty, new_avg, pf_id, symbol))
                else: # SELL
                    new_qty = current_qty - quantity
                    if new_qty <= 0:
                        cursor.execute(cls._adapt_query_static("DELETE FROM holdings WHERE portfolio_id = ? AND symbol = ?"), (pf_id, symbol))
                    else:
                        cursor.execute(cls._adapt_query_static("UPDATE holdings SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE portfolio_id = ? AND symbol = ?"), (new_qty, pf_id, symbol))
            else:
                if side.upper() == 'BUY':
                    h_id = f"h_{uuid.uuid4().hex[:8]}"
                    cursor.execute(
                        cls._adapt_query_static("INSERT INTO holdings (id, portfolio_id, symbol, quantity, avg_entry_price) VALUES (?, ?, ?, ?, ?)"),
                        (h_id, pf_id, symbol, quantity, price)
                    )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating holding: {e}")
            return False
        finally:
            conn.close()

    @classmethod
    def record_order(cls, user_id: str, symbol: str, side: str, qty: float, price: float, status: str, order_id: str = None) -> str:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(cls._adapt_query_static("SELECT id FROM portfolios WHERE user_id = ? LIMIT 1"), (user_id,))
            pf = cursor.fetchone()
            if not pf:
                return None
            pf_id = pf[0]

            if not order_id:
                order_id = f"ord_{uuid.uuid4().hex[:10]}"

            cursor.execute(
                cls._adapt_query_static("INSERT INTO orders (id, portfolio_id, symbol, side, order_type, quantity, price, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"),
                (order_id, pf_id, symbol, side, "MARKET", qty, price, status)
            )
            
            if status == "FILLED":
                exec_id = f"exec_{uuid.uuid4().hex[:10]}"
                cursor.execute(
                    cls._adapt_query_static("INSERT INTO executions (id, order_id, symbol, side, quantity, price) VALUES (?, ?, ?, ?, ?, ?)"),
                    (exec_id, order_id, symbol, side, qty, price)
                )

            conn.commit()
            return order_id
        except Exception as e:
            print(f"Error recording order: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def _adapt_query_static(cls, sql: str) -> str:
        if IS_POSTGRES:
            return sql.replace("?", "%s").replace("INSERT OR REPLACE", "INSERT").replace("INSERT OR IGNORE", "INSERT")
        return sql
"""

if "def update_holding" not in content:
    content += db_methods
    with open('webui/db.py', 'w') as f:
        f.write(content)
