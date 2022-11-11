#!/usr/bin/env python

#
# テストベッドファイルからデバイスを取り出します。
# そのデバイスに接続します。
# コマンドを打ち込んで結果を画面に表示します。
#

# usage: ex10.execute.py [-h] [--testbed TESTBED]
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

# execute()でコマンドを投げ込みます
# outputにはその応答が格納されます
output = uut.execute('show version')

# 画面に応答を表示します
from pprint import pprint
pprint(output)
