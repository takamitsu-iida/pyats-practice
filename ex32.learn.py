#!/usr/bin/env python

#
# 抽象的な機能名'stp'を指定して学習させる
#

# usage: ex32.learn.py [-h] [--testbed TESTBED]
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
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

# テストベッドをロードします
testbed = load(args.testbed)

learnt = {}
for name, dev in testbed.devices.items():
    if dev.type == 'switch':
        try:
            # そのデバイスに接続します
            dev.connect()

            # stpを学習します
            learnt[name] = dev.learn('stp')

            # そのデバイスとの接続を切ります
            dev.disconnect()

        except (TimeoutError, ConnectionError, SubCommandFailure) as e:
            print(e)

for name, stp in learnt.items():
    print(name)
    pprint(stp.info)
