#!/usr/bin/env python

import os
from pyats.easypy import run

TEST_SCRIPT = "example_script.py"

def main():
    test_path = os.path.dirname(os.path.abspath(__file__))
    testscript = os.path.join(test_path, TEST_SCRIPT)

    # Execute the testscript
    run(testscript=testscript)
