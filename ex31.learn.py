#!/usr/bin/env python

#
# 抽象的な機能名を指定して学習させる
#

import os
import sys
from pprint import pprint

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

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect
uut.connect(via='console')

# 機種固有のInterfaceをインポートする場合
# from genie.libs.ops.interface.ios.interface import Interface
# from genie.libs.ops.interface.iosxr.interface import Interface
# from genie.libs.ops.interface.iosxe.interface import Interface

# 装置情報から自動で機種にあったInterfaceをロードする場合
from genie.ops.utils import get_ops
Interface = get_ops('interface', uut)

# get ops object
intf = Interface(device=uut)

# learn all interfaces
intf.learn()

# disconnect
if uut.is_connected():
    uut.disconnect()

# learnt correctly?
assert intf.info

# intf object should be like this
# {'info': {'interface_name': {

intf_list = intf.info.keys()

if intf_list:
    print('learnt interfaces')
    pprint(intf_list)

    # print only Gig1
    pprint(intf.info['GigabitEthernet1'])

    # or print all interfaces
    # pprint(intf.info)

else:
    print('interface not found')
