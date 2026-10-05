import re

with open('webui/agents_engine/orchestrator.py', 'r') as f:
    content = f.read()

content = re.sub(
    r'def run_cycle\(\s*self,\s*symbol:\s*str,\s*timeframe:\s*str = "1d",\s*pred_len:\s*int = 14,\s*allow_trading:\s*bool = True,\s*analysis_id:\s*Optional\[str\] = None\s*\)',
    r'def run_cycle(\n        self,\n        symbol: str,\n        timeframe: str = "1d",\n        pred_len: int = 14,\n        allow_trading: bool = True,\n        analysis_id: Optional[str] = None,\n        user_id: str = None\n    )',
    content
)

content = content.replace("res = self.execute(symbol=symbol, timeframe=timeframe)", "res = self.execute(symbol=symbol, timeframe=timeframe, user_id=user_id)")

with open('webui/agents_engine/orchestrator.py', 'w') as f:
    f.write(content)
