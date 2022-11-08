#!/usr/bin/env python

#
# 単体のコマンドをパースする
#

# usage: ex20.parse.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

# import Genie
from genie.testbed import load

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect
uut.connect()

# parse "show version"
output = uut.parse('show version')

# disconnect
if uut.is_connected():
    uut.disconnect()

from pprint import pprint
pprint(output)
