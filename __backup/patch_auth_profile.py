import re

with open('webui/app.py', 'r') as f:
    content = f.read()

new_routes = """
@app.route('/api/profile', methods=['PATCH'])
@login_required
def api_profile_patch():
    user = get_current_user()
    data = request.get_json() or {}
    new_password = data.get('password')
    
    if new_password:
        if len(new_password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
        
        conn, _ = get_db_connection()
        try:
            cursor = conn.cursor()
            pwd_hash = hash_password(new_password)
            cursor.execute(_adapt_query("UPDATE users SET password_hash = ? WHERE id = ?"), (pwd_hash, user['id']))
            conn.commit()
            return jsonify({"success": True, "message": "Password updated"})
        except Exception as e:
            print("Error updating password:", e)
            return jsonify({"success": False, "error": "Database error"}), 500
        finally:
            conn.close()
            
    return jsonify({"success": True})
"""

content += "\n" + new_routes

with open('webui/app.py', 'w') as f:
    f.write(content)
