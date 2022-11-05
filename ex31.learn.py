#!/usr/bin/env python

#
# interfaceの状態を学習させる
#

# usage: ex31.learn.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
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

# 学習した結果の辞書型はinfoキーで入手する
# pprint(intf.info)
# {'GigabitEthernet1': {},
#  'GigabitEthernet2': {},
#  'GigabitEthernet3': {},

# 学習できているか確認
assert intf.info

# インタフェース名の一覧はkeys()で入手できる
# この一覧はソートされていないので、必要ならソートする
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
