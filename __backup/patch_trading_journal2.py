import re

with open('webui/agents_engine/trading_journal.py', 'r') as f:
    content = f.read()

bad_def = """    def record_prediction(self,
                          user_id: str = None,
                          symbol: str,"""
good_def = """    def record_prediction(self,
                          symbol: str,"""

content = content.replace(bad_def, good_def)

content = content.replace("position_sizing: Optional[Dict[str, Any]] = None)", "position_sizing: Optional[Dict[str, Any]] = None, user_id: str = None)")

with open('webui/agents_engine/trading_journal.py', 'w') as f:
    f.write(content)

