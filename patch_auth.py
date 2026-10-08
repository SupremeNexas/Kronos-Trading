import os

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    new_content = content.replace(
"""def get_current_user():
    # First check cookies for http-only secure session""",
"""def get_current_user():
    # Bypass auth if LOCAL_TRADING_MODE is specified and environment is not production
    is_prod = os.environ.get("RENDER") is not None
    local_mode_enabled = os.environ.get("LOCAL_TRADING_MODE", "true").lower() == "true"
    if not is_prod and local_mode_enabled:
        return {"id": "user_local_001", "email": "local@kronos.ai", "name": "Local Trader", "role": "admin", "created_at": "2026-01-01T00:00:00Z"}
        
    # First check cookies for http-only secure session"""
    )
    
    with open(filepath, 'w') as f:
        f.write(new_content)
        
patch_file('webui/app.py')
