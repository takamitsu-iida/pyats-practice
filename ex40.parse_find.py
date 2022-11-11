#!/usr/bin/env python

#
# find interfaces where out_pkts is 0.
#

# usage: ex40.parse_find.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse

from pprint import pprint

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

# parse
parsed = uut.parse('show interfaces')

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()

# パース結果を表示します
for name, data in parsed.items():
    pprint(data)

# 力技で見つける方法
for name, data in parsed.items():
    if 'counters' in data:
       if 'out_pkts' in data['counters']:
           if parsed[name]['counters']['out_pkts'] == 0 :
                print(f"{name} is not used.")
                # uut.configure('int {}\n shutdown'.format(name))

# pyATSのfindを使って見つける方法
# https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html

from pyats.utils.objects import R, find

# このキー階層の値を採取したい
# {interface_name: {'counters': {'out_pkts': 0

req = R(['(.*)', 'counters', 'out_pkts', 0])
found = find(parsed, req, filter_=False)
pprint(found)
