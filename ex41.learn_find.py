#!/usr/bin/env python

# pyatsのfindを使ってインタフェースを見つける
# https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

# 機種固有のInterfaceをインポートする場合
# from genie.libs.ops.interface.ios.interface import Interface
# from genie.libs.ops.interface.iosxr.interface import Interface
# from genie.libs.ops.interface.iosxe.interface import Interface

# 装置情報から自動で機種にあったInterfaceをロードする場合
from genie.ops.utils import get_ops
Interface = get_ops('interface', uut)

intf = Interface(device=uut)
intf.learn()

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