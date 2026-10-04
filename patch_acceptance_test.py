with open("acceptance_test.py", "r") as f:
    text = f.read()

import re
text = re.sub(r'orchestrator = AgentEngineOrchestrator\(broker=broker, predictor=None\)\s*orchestrator\.forecast_desk\.forecast = lambda \*args, \*\*kwargs: ForecastDistribution\([\s\S]*?source_timestamp=datetime\.datetime\.now\(\)\s*\)', 'orchestrator = AgentEngineOrchestrator(broker=broker, predictor=predictor)', text)

with open("acceptance_test.py", "w") as f:
    f.write(text)
