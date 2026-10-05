import re
import os

with open('webui/app.py', 'r') as f:
    content = f.read()

# Add get_current_user helper
auth_helper = """
from flask import request, jsonify, make_response
from webui.db import DatabaseManager

def get_current_user():
    # First check cookies for http-only secure session
    session_token = request.cookies.get('session_token')
    if session_token:
        user = DatabaseManager.get_user_from_session(session_token)
        if user:
            return user
            
    # Then check Auth Bearer token if API access
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        user = DatabaseManager.get_user_from_session(token)
        if user:
            return user
            
    return None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function
"""

if 'def get_current_user():' not in content:
    content = content.replace('from flask import Flask, request, jsonify', 'from flask import Flask, request, jsonify, make_response')
    content = content.replace("app = Flask(__name__)", "app = Flask(__name__)\n\n" + auth_helper.strip())

# Patch CORS for credentials
if "CORS(app, resources={r\"/*\": {\"origins\": \"*\"}})" in content:
    content = content.replace(
        "CORS(app, resources={r\"/*\": {\"origins\": \"*\"}})", 
        "CORS(app, resources={r\"/*\": {\"origins\": [\"http://localhost:3000\", \"http://localhost:7070\"], \"supports_credentials\": True}})"
    )

# Implement /api/auth/me, logout, patch /api/auth/login, /api/auth/register
new_auth_endpoints = """
@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()

    if not email or len(password) < 6:
        return jsonify({"success": False, "error": "Valid email and password (min 6 characters) required"}), 400

    res = DatabaseManager.create_user(email=email, password=password, name=name or email.split('@')[0])
    if res.get("success"):
        # Auto login
        user_id = res['user']['id']
        session_token = DatabaseManager.create_session(user_id)
        resp = make_response(jsonify(res))
        resp.set_cookie('session_token', session_token, httponly=True, secure=True, samesite='None', max_age=7*24*3600)
        return resp
    return jsonify(res), 400

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400

    res = DatabaseManager.authenticate_user(email=email, password=password)
    if res.get("success"):
        user_id = res['user']['id']
        session_token = DatabaseManager.create_session(user_id)
        resp = make_response(jsonify(res))
        resp.set_cookie('session_token', session_token, httponly=True, secure=True, samesite='None', max_age=7*24*3600)
        return resp
    return jsonify(res), 401
    
@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    session_token = request.cookies.get('session_token')
    if session_token:
        DatabaseManager.delete_session(session_token)
    resp = make_response(jsonify({"success": True}))
    resp.set_cookie('session_token', '', expires=0, httponly=True, secure=True, samesite='None')
    return resp

@app.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    user = get_current_user()
    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "error": "Not authenticated"}), 401
"""

content = re.sub(r"@app\.route\('/api/auth/register'.*?def api_auth_me\(\):.*?return jsonify\(\{\"success\": True, \"user\": user\}\)", new_auth_endpoints.strip(), content, flags=re.DOTALL)


# Write it out
with open('webui/app.py', 'w') as f:
    f.write(content)
