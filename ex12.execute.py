#!/usr/bin/env python

#
# 装置に接続して 'show running-config' を打ち込む例です。
#

# usage: ex12.execute.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
import sys
import os

#
# python標準のtelnetlibではなく、バッファを大きくしたtelnetlibを先に読み込みます
#
def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

if not here('./lib') in sys.path:
  sys.path.insert(0, here('./lib'))

import telnetlib
if telnetlib.MODIFIED_BY:
    print('modified telnetlib is loaded.')

# このスクリプトを実行するときに --testbed を指定することで読み込むテストベッドファイルを切り替えます
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

# Genieライブラリからテストベッドをロードする関数をインポートします
from genie.testbed import load
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

# テストベッドをロードします
testbed = load(args.testbed)

# 名前（もしくはエイリアス）が'uut'になっている装置を取り出します（uut = unit under test）
uut = testbed.devices['uut']

try:
    # そのデバイスに接続します
    uut.connect()
except (TimeoutError, ConnectionError) as e:
    print(e)
    sys.exit(1)

try:
    # コマンドを打ち込みます
    output = uut.execute('show running-config')
except SubCommandFailure as e:
    print(e)

if uut.is_connected():
    # デバイスとの接続を切ります
    uut.disconnect()

# 画面に応答を表示します
from pprint import pprint
pprint(output)
