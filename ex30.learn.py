#!/usr/bin/env python

#
# 抽象的な機能名を指定して学習
#

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

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
