#!/usr/bin/env python

#
# poll interface status
#
# see
# https://pubhub.devnetcloud.com/media/genie-docs/docs/userguide/Ops/user/ops.html

# usage: ex43.learn_poll.py [-h] [--testbed TESTBED]
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

# 機種固有のInterfaceをインポートする場合
# from genie.libs.ops.interface.ios.interface import Interface
# from genie.libs.ops.interface.iosxr.interface import Interface
# from genie.libs.ops.interface.iosxe.interface import Interface

# 装置情報から自動で機種にあったInterfaceをロードする場合
from genie.ops.utils import get_ops

# verify at least one interface is up, or raise Exception
def verify_interface_status(obj):
    # make sure interface has learnt
    assert obj.info

    for name in obj.info.keys():
        oper_status = obj.info[name].get('oper_status', None)
        if oper_status == 'up':
            print("verified successfully")
            return

    raise Exception("Could not find any up interface")

# テストベッドをロードします
testbed = load(args.testbed)

# 名前（もしくはエイリアス）が'uut'になっている装置を取り出します（uut = unit under test）
uut = testbed.devices['uut']

# そのデバイスに接続します
uut.connect()

# 機種にあったInterfaceクラスをロードする
Interface = get_ops('interface', uut)

intf = Interface(device=uut)

# 少なくとも１つのインタフェースが'up'になるまで
#  - 繰り返す回数 3回
#  - 5秒間隔
# で実行します
try:
    intf.learn_poll(verify=verify_interface_status, sleep=5, attempt=3)
except StopIteration as e:
    print(e)

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()
