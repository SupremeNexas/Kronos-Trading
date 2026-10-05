import re

with open("webui/forecast_engine.py", "r") as f:
    text = f.read()

# I am completely overwriting it since it is very outdated and doesn't use the KRONOS model.
