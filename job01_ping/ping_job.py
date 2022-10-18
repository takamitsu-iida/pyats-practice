#!/usr/bin/env python

import os

from pyats.easypy import run

# List of addresses to ping
ping_list = [
    '192.168.12.1',
    '192.168.12.2',
    '192.168.13.1',
    '192.168.13.3',
    '192.168.24.2',
    '192.168.24.4',
    '192.168.34.3',
    '192.168.34.4',
    '192.168.255.1',
    '192.168.255.2',
    '192.168.255.3',
    '192.168.255.4'
]

SCRIPT_FILE = 'ping_test.py'
SCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_PATH = os.path.join(SCRIPT_DIR, SCRIPT_FILE)

def main(runtime):
    """job file entrypoint"""

    # run script, pass arguments to script as parameters
    run(
        testscript=SCRIPT_PATH,
        runtime=runtime,
        taskid='Ping',
        ping_list=ping_list
    )
