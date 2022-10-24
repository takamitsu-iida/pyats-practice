#!/usr/bin/env python

#
# 抽象的な機能名を指定して学習させる
#

# usage: ex32.learn.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse

from pprint import pprint

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

learnt = {}
for name, dev in testbed.devices.items():
    if dev.type == 'Switch':
        try:
            # connect
            dev.connect(via='console')

            # learn
            learnt[name] = dev.learn('stp')

            # disconnect
            dev.disconnect()

        except (TimeoutError, ConnectionError, SubCommandFailure) as e:
            print(e)

for name, stp in learnt.items():
    print(name)
    pprint(stp.info)
