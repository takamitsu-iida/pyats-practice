#!/usr/bin/env python

#
# compare two ops objects
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html
#

# usage: ex60.diff.py [-h] [--testbed TESTBED]
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
from genie.utils.diff import Diff

# テストベッドをロードします
testbed = load(args.testbed)

# 名前（もしくはエイリアス）が'uut'になっている装置を取り出します（uut = unit under test）
uut = testbed.devices['uut']

# そのデバイスに接続します
uut.connect()

# 変更前のコンフィグを学習します
pre_conf = uut.learn('config')

# OSPFの設定を変更します
#  - Gig1のコストを100から10に変更
uut.configure('''
interface Gig1
ip ospf cost 10
exit
''')

# 変更後のコンフィグを学習します
post_conf = uut.learn('config')

# OSPF設定をもとに戻します
uut.configure('''
interface Gig1
ip ospf cost 100
exit
''')

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()

# コンフィグの差分を検出して表示します
config_diff = Diff(pre_conf, post_conf)
config_diff.findDiff()
print(config_diff)
