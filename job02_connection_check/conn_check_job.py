#!/usr/bin/env python

from curses.ascii import TAB
import os

from pyats.easypy import run

SCRIPT_FILE = 'conn_check_test.py'
SCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_PATH = os.path.join(SCRIPT_DIR, SCRIPT_FILE)

TASK_ID = 'Connection'

def main(runtime):
    run(
        testscript=SCRIPT_PATH,
        runtime=runtime,
        taskid=TASK_ID
    )
