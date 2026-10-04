import requests
import json
try:
    print(requests.get("http://localhost:7070/api/lab/system-status").text)
except Exception as e:
    print(e)
