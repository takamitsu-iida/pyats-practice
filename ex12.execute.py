#!/usr/bin/env python

#
# execute 'show running-config'
#

# usage: ex12.execute.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
import sys
import os

#
# overwrite standard telnetlib
#
def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

if not here('./lib') in sys.path:
  sys.path.insert(0, here('./lib'))

import telnetlib
if telnetlib.MODIFIED_BY:
    print('modified telnetlib is loaded.')

# script args
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

# import Genie
from genie.testbed import load
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect to the uut
try:
    uut.connect()
except (TimeoutError, ConnectionError) as e:
    print(e)
    sys.exit(1)

# execute command
try:
    output = uut.execute('show running-config')
except SubCommandFailure as e:
    print(e)

# disconnect from the uut
if uut.is_connected():
    uut.disconnect()

from pprint import pprint
pprint(output)
