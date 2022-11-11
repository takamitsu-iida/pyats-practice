#!/usr/bin/env python

#
# ex10.execute.pyと同じもので、例外処理を加えたものです。
# raiseされる例外を調べるのは面倒なのでこちらを流用するとよいでしょう。
#

# usage: ex11.execute.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

from genie.testbed import load
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from unicon.core.errors import SubCommandFailure

testbed = load(args.testbed)

uut = testbed.devices['uut']

try:
    uut.connect()
except (TimeoutError, StateMachineError, ConnectionError) as e:
    print(e)
    sys.exit(1)

try:
    output = uut.execute('show version')
except SubCommandFailure as e:
    print(e)

if uut.is_connected():
    uut.disconnect()

from pprint import pprint
pprint(output)
