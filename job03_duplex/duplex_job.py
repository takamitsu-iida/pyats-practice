#!/usr/bin/env python

import os

from pyats.easypy import run

SCRIPT_PATH = os.path.dirname(__file__)

def main(runtime):
    """job file entrypoint"""

    run(
        testscript=os.path.join(SCRIPT_PATH, "duplex_test.py"),
        runtime=runtime,
        taskid="Duplex Test",
    )
