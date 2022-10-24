#!/usr/bin/env python

#
# same as ex10.execute.py
#

# usage: ex11.execute.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
import sys

# script args
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

# import Genie
from genie.testbed import load
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from unicon.core.errors import SubCommandFailure

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect to the uut
try:
    uut.connect(via='console')
except (TimeoutError, StateMachineError, ConnectionError) as e:
    print(e)
    sys.exit(1)

# execute command
try:
    output = uut.execute('show version')
except SubCommandFailure as e:
    print(e)

# disconnect from the uut
if uut.is_connected():
    uut.disconnect()

# print output
from pprint import pprint
pprint(output)
