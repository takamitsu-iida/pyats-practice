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

# pyatsのfindを使ってupになっているインタフェースを見つける
# https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html
#
# Rに渡す配列は、辞書型のキーの順番で、最後の要素だけは一致させる値になる
#
from pyats.utils.objects import R, find
req = R(['info', '(.*)', 'oper_status', 'up'])
intf_up = find(intf, req, filter_=False)
pprint(intf_up)
