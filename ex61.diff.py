#!/usr/bin/env python

#
# compare two ops objects
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html
#

# usage: ex61.diff.py [-h] [--testbed TESTBED]
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

# learn ospf state
pre_ospf = uut.learn('ospf')

# change ospf config
# cost 100 -> 10
uut.configure('''
interface Gig1
ip ospf cost 10
exit
''')

# learn current ospf state
post_ospf = uut.learn('ospf')

# revert ospf config
uut.configure('''
interface Gig1
ip ospf cost 100
exit
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

diff = post_ospf.diff(pre_ospf)
diff.findDiff()
print(diff)

print('='*10)
print('WITH EXCLUDE')
print('='*10)

# OSPFではこれらを差分計算の対象から除外
exclude = [
    'database',
    'dead_timer',
    'hello_timer',
    'statistics'
    ]

diff = post_ospf.diff(pre_ospf, exclude=exclude)
diff.findDiff
print(diff)
