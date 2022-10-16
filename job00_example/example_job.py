#!/usr/bin/env python

#
# To run the job:
# pyats run job --testbed-file lab.yml example_job.py
#

import os
from pyats.easypy import run

TEST_SCRIPT = "example_script.py"

def main():
    # Find the location of the script in relation to the job file
    test_path = os.path.dirname(os.path.abspath(__file__))
    testscript = os.path.join(test_path, TEST_SCRIPT)

    # Execute the testscript
    run(testscript=testscript)
