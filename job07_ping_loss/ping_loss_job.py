#!/usr/bin/env python

import os

from pyats.easypy import run

SCRIPT = 'ping_loss_test.py'
TASK_ID = 'ping_loss'
DATAFILE = 'datafile.yml'

SCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_PATH = os.path.join(SCRIPT_DIR, SCRIPT)
DATAFILE_PATH = os.path.join(SCRIPT_DIR, DATAFILE)

def main(runtime):
    """job file entrypoint"""

    # run()に渡す引数
    run_args = {
        'runtime': runtime,
        'taskid': TASK_ID,
        'testscript': SCRIPT_PATH
    }

    # データファイルが存在するなら引数に追加
    if os.path.exists(DATAFILE_PATH):
        run_args.update({'datafile': DATAFILE_PATH})

    # run script
    run(**run_args)
