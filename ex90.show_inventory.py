#!/usr/bin/env python

import argparse
import sys

from pprint import pprint

# このスクリプトを実行するときに --testbed を指定することで読み込むテストベッドファイルを切り替えます
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

# Genieライブラリからテストベッドをロードする関数をインポートします
from genie.testbed import load

# 例外クラスをインポートします
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from unicon.core.errors import SubCommandFailure

# テストベッドをロードします
testbed = load(args.testbed)

# 名前（もしくはエイリアス）が'uut'になっている装置を取り出します（uut = unit under test）
uut = testbed.devices['uut']

try:
    # そのデバイスに接続します
    uut.connect()
except (TimeoutError, StateMachineError, ConnectionError) as e:
    print(e)
    sys.exit(1)

try:
    # 独自のパーサーでパースします
    from myparser.show_inventory.show_inventory_parser import MyShowInventory
    myparser = MyShowInventory(device=uut)
    parsed = myparser.parse()
except SubCommandFailure as e:
    print(e)

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()

# 画面に表示します
pprint(parsed)
