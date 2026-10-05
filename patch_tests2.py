with open("tests/test_user_isolation.py", 'r') as f:
    content = f.read()

content = content.replace('@pytest.fixture\ndef users(client):', '@pytest.fixture(scope="module")\ndef users(client):')

import uuid
import re

content = re.sub(
    r"'scan_a'",
    f"f'scan_{{uuid.uuid4().hex[:6]}}'",
    content
)

with open("tests/test_user_isolation.py", 'w') as f:
    f.write(content)
