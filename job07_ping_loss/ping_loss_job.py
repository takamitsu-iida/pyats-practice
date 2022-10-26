#!/usr/bin/env python

import os

from pyats.easypy import run

SCRIPT_FILE = 'ping_loss_test.py'
SCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_PATH = os.path.join(SCRIPT_DIR, SCRIPT_FILE)

TASK_ID = 'DownUp'

def main(runtime):
    """job file entrypoint"""

    # run script, pass arguments to script as parameters
    run(
        testscript=SCRIPT_PATH,
        runtime=runtime,
        taskid=TASK_ID
    )
