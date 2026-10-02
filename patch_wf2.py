with open("examples/paper_trade_workflow.py", "r") as f:
    c = f.read()

c = c.replace("from webui.broker import BrokerAdapter", "from webui.broker_service_alpaca import AlpacaBrokerAdapter")
c = c.replace("from webui.forecast_engine import PredictorAdapter", "from webui.app import predictor")
c = c.replace("broker = BrokerAdapter()", "broker = AlpacaBrokerAdapter()")
c = c.replace("predictor = PredictorAdapter()", "")

with open("examples/paper_trade_workflow.py", "w") as f:
    f.write(c)
