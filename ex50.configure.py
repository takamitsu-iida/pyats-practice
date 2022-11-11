#!/usr/bin/env python

#
# configure directly
#

# usage: ex50.configure.py [-h] [--testbed TESTBED]
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

# configure
output = uut.configure('''
interface Gig1
description "configured by pyats"
exit
interface Gig2
description "configured by pyats"
exit
''')

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()

# 画面に表示します
from pprint import pprint
pprint(output)
