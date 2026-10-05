import os
import sys
import json
os.environ['RENDER'] = 'true'
sys.path.append(os.path.join(os.path.dirname(__file__), 'webui'))
from webui.app import app
with app.test_client() as client:
    resp = client.post('/api/verification/run')
    print(json.dumps(resp.get_json(), indent=2))
