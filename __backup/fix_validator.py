with open("webui/agents_engine/trading_journal.py", "r") as f:
    text = f.read()

# Make sure validation parsing works with dictionaries too.
# The `entry["validation"]` in journal is populated from `validation_results` argument.
