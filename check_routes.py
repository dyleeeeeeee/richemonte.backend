#!/usr/bin/env python3
from app import create_app

app = create_app()
print('=== REGISTERED ROUTES ===')
for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f'{methods:<20} {rule.rule:<50}')
