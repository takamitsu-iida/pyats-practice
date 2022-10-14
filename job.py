#!/usr/bin/env python

# Example: job.py
# -------------------
#
#   a simple job file for the script above

# pyats run job job.py --testbed-file lab-testbed.yml --html-logs

from pyats.easypy import run

def main():

    # run api launches a testscript as an individual task.
    run('conn_check.py')