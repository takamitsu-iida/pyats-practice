#!/usr/bin/env python

#
# 抽象的な機能名'routing'を指定して学習
#

# usage: ex30.learn.py [-h] [--testbed TESTBED]
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
uut.connect(via='console')

# learn routing table
routing = uut.learn('routing')

# disconnect
if uut.is_connected():
    uut.disconnect()

from pprint import pprint
pprint(routing.info)
