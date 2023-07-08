#!/usr/bin/env python3

import os
import sys

def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


WF_DATA = os.getenv('alfred_workflow_data')
PREFIXES = os.getenv('MyPrefixes')
WF_CUSTOM = f"{WF_DATA}/custom.csv"
ALFRED_PREFS = os.getenv('alfred_preferences')


if not os.path.exists(WF_DATA):
    os.makedirs(WF_DATA)

DIRNAME = f'{ALFRED_PREFS}/workflows'







    