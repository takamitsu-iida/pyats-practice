#!/usr/bin/env python

#
# compare two ops objects
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html
#

# usage: ex62.diff.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
import os
import sys

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

# テストベッドをロードします
testbed = load(args.testbed)

# 名前（もしくはエイリアス）が'uut'になっている装置を取り出します（uut = unit under test）
uut = testbed.devices['uut']

# そのデバイスに接続します
uut.connect()

# learn routing table
pre_routing = uut.learn('routing')

# change static route
uut.configure('''
ip route 192.168.100.0 255.255.255.0 null 0
''')

# learn current routing table
post_routing = uut.learn('routing')

# revert static route
uut.configure('''
no ip route 192.168.100.0 255.255.255.0 null 0
''')

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()

# from genie.utils.diff import Diff
# diff = Diff(pre_ospf, post_ospf)
# diff.findDiff()
# print(diff)

print('='*10)
print('WITHOUT EXCLUDE')
print('='*10)

diff = post_routing.diff(pre_routing)
diff.findDiff()
print(diff)

print('='*10)
print('WITH EXCLUDE')
print('='*10)

# routingではこれらを差分計算の対象から除外
exclude=['updated']

diff = post_routing.diff(pre_routing, exclude=exclude)
diff.findDiff
print(diff)
