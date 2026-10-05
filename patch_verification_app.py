import os

app_file = os.path.join("webui", "app.py")
with open(app_file, 'r') as f:
    content = f.read()

# Make sure we don't insert it twice
if "verification_bp" not in content:
    idx = content.find("if __name__ == '__main__':")
    
    insert_str = """
# Setup System Proof Blueprint
try:
    from verification_routes import verification_bp
    app.register_blueprint(verification_bp)
    print("✅ System Proof Verification Center registered")
except Exception as e:
    print(f"Failed to load System Proof Verification Blueprint: {e}")

"""
    new_content = content[:idx] + insert_str + content[idx:]
    with open(app_file, 'w') as f:
        f.write(new_content)
    print("Patched app.py")
else:
    print("Already patched app.py")

