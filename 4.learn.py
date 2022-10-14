#!/usr/bin/env python

# Import Genie
from genie.conf import Genie

testbed = Genie.init('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

# インタフェースを学習させるには機種の情報が必要
# ios, iosxr, iosxe
from genie.libs.ops.interface.iosxe.interface import Interface

intf = Interface(device=uut)
intf.learn()

from pprint import pprint
pprint(intf.info)

# Let's get all the up interfaces
from pyats.utils.objects import R, find
req1 = R(['info', '(.*)', 'oper_status', 'up'])
intf_up = find(intf, req1, filter_=False)
pprint(intf_up)
