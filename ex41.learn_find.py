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

# このスクリプトを実行するときに --testbed を指定することで読み込むテストベッドファイルを切り替えます
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

# Genieライブラリからテストベッドをロードする関数をインポートします
from genie.testbed import load

# テストベッドをロードします
testbed = load(args.testbed)

# 名前（もしくはエイリアス）が'uut'になっている装置を取り出します（uut = unit under test）
uut = testbed.devices['uut']

# そのデバイスに接続します
uut.connect()

# 機種固有のInterfaceをインポートする場合
# from genie.libs.ops.interface.ios.interface import Interface
# from genie.libs.ops.interface.iosxr.interface import Interface
# from genie.libs.ops.interface.iosxe.interface import Interface

# 装置情報から自動で機種にあったInterfaceをロードする場合
from genie.ops.utils import get_ops
Interface = get_ops('interface', uut)
intf = Interface(device=uut)

# インタフェースを学習します
intf.learn()

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()

# 画面に表示します
from pprint import pprint
pprint(intf.info)

from pyats.utils.objects import R, find

# このキー階層の値を採取したい
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