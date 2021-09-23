#!/usr/bin/env python
from applescript import tell

i = 0
while i < 200:
    cmd1 = "cd /Users/zorankokovic/Development/github/rockiot_project"
    cmd2 = "source venv/bin/activate"
    cmd3 = "cd rockiot_demo"
    cmd4 = "export DEMO_SLEEP_SECONDS=60"
    cmd5 = f"python mqtt_demo.py device999{i} device999{i}pass"
    cmd = f'{cmd1} && {cmd2} && {cmd3} && {cmd4} && {cmd5}'
    tell.app('Terminal', 'do script "' + cmd + '"')
    i += 1
