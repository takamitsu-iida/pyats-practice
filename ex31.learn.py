#!/usr/bin/env python

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

# インタフェースを学習させるには機種の情報が必要
# ios, iosxr, iosxe
from genie.libs.ops.interface.iosxe.interface import Interface

intf = Interface(device=uut)
intf.learn()

from pprint import pprint
pprint(intf.info)
