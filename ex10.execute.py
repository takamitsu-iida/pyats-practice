#!/usr/bin/env python

#
# connect to the uut and execute commnad
#

# usage: ex10.execute.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse

# script args
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

# connect to the uut
uut.connect(via='console')

# execute command
output = uut.execute('show version')

# print output
from pprint import pprint
pprint(output)
