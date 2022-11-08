#!/usr/bin/env python

import argparse
import sys

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
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from unicon.core.errors import SubCommandFailure

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect to the uut
try:
    uut.connect()
except (TimeoutError, StateMachineError, ConnectionError) as e:
    print(e)
    sys.exit(1)

# parse 'show inventory'
try:
    from myparser.show_inventory.show_inventory_parser import MyShowInventory
    myparser = MyShowInventory(device=uut)
    parsed = myparser.parse()
except SubCommandFailure as e:
    print(e)

# disconnect from the uut
if uut.is_connected():
    uut.disconnect()

pprint(parsed)
