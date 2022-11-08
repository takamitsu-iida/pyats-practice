#!/usr/bin/env python

#
# pyatsのfindを使ってインタフェースを見つける
# https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html
#

# usage: ex41.learn_find.py [-h] [--testbed TESTBED]
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

# connect
uut.connect()

# 機種固有のInterfaceをインポートする場合
# from genie.libs.ops.interface.ios.interface import Interface
# from genie.libs.ops.interface.iosxr.interface import Interface
# from genie.libs.ops.interface.iosxe.interface import Interface

# 装置情報から自動で機種にあったInterfaceをロードする場合
from genie.ops.utils import get_ops
Interface = get_ops('interface', uut)
intf = Interface(device=uut)

# learn
intf.learn()

# disconnect
if uut.is_connected():
    uut.disconnect()

from pprint import pprint
pprint(intf.info)

from pyats.utils.objects import R, find

# from
# {'info': {'interface name': {'oper_status': 'up'

# Rに渡す配列は、辞書型のキーの順番で、最後の要素だけは一致させる値になる

# oper_statusがupのインタフェース
req = R(['info', '(.*)', 'oper_status', 'up'])
intf_up = find(intf, req, filter_=False)
print('up interfaces')
pprint(intf_up)

print('')

# duplexがfullのインタフェース
req2 = R(['info', '(.*)', 'duplex_mode', 'full'])
intf_full = find(intf, req2, filter_=False)
print('full duplex interfaces')
pprint(intf_full)

print('')

# oper_statusがupで、かつ、duplexがfullのインタフェース
req3 = [
    R(['info', '(?P<interface>.*)', 'oper_status', 'up']),
    R(['info', '(?P<interface>.*)', 'duplex_mode', 'full'])
]
intf_up_full = find(intf, *req3, filter_=False)
print("up and full duplex interfaces")
pprint(intf_up_full)