#!/usr/bin/env python

#
# デバイス固有のAPIにどういったものがあるのかを確認します。
#
# このURLでサポートしているAPIの一覧を確認できます。
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/apis
#

# 実行結果は
# ./ex80.api.py > output/ex80.log
# として残してあります。

from pprint import pprint

import argparse

# このスクリプトを実行するときに --testbed を指定することで読み込むテストベッドファイルを切り替えます
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

# Genieライブラリからテストベッドをロードする関数をインポートします
from genie.testbed import load

# テストベッドをロードします
testbed = load(args.testbed)

# uutという名前（エイリアス）の装置を取り出します
uut = testbed.devices['uut']

# uut.apiの中にあるインスタンスを表示します
pprint(dir(uut.api))
