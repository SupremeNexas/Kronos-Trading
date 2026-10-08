import re

with open('webui/agents_engine/orchestrator.py', 'r') as f:
    content = f.read()

# Add user_id to process_symbol and execute
content = re.sub(r'def execute\(self, symbol: str, timeframe: str = "1d"\)', 'def execute(self, symbol: str, timeframe: str = "1d", user_id: str = None)', content)
content = re.sub(r'def process_symbol\(self, symbol: str, timeframe: str = "1d"\)', 'def process_symbol(self, symbol: str, timeframe: str = "1d", user_id: str = None)', content)

# pass user_id down
content = content.replace("flow_data = self.process_symbol(symbol, timeframe)", "flow_data = self.process_symbol(symbol, timeframe, user_id=user_id)")

content = content.replace("journal_id = self.trading_journal.record_prediction(", "journal_id = self.trading_journal.record_prediction(\\n                user_id=user_id,")

with open('webui/agents_engine/orchestrator.py', 'w') as f:
    f.write(content)
