#!/usr/bin/env python

import os

from pyats.easypy import run

SCRIPT_FILE = 'route_test.py'
SCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_PATH = os.path.join(SCRIPT_DIR, SCRIPT_FILE)

def main(runtime):
    """job file entrypoint"""

    # run script, pass arguments to script as parameters
    run(
        testscript=SCRIPT_PATH,
        runtime=runtime,
        taskid='Ping'
    )