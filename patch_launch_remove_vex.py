import json

with open('.claude/launch.json', 'r') as f:
    config = json.load(f)

config['configurations'] = [c for c in config['configurations'] if c.get('name') != 'vex-hero-dev']

with open('.claude/launch.json', 'w') as f:
    json.dump(config, f, indent=2)
