#!/usr/bin/env python

#
# configure static route
#
# ドキュメントがないので使い方はソースコードを参照
# https://github.com/CiscoTestAutomation/genielibs/blob/master/pkgs/conf-pkg/src/genie/libs/conf/static_routing/iosxe/tests/test_static_routing.py

# usage: ex52.configure.py [-h] [--testbed TESTBED]
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

from genie.libs.conf.static_routing.static_routing import StaticRouting

static_routing = StaticRouting()

# 1行で書くと見づらい
# static_routing.device_attr[uut].vrf_attr['default'].address_family_attr['ipv4'].route_attr['10.10.10.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'

# ipv4オブジェクトを取り出す
ipv4 = static_routing.device_attr[uut].vrf_attr['default'].address_family_attr['ipv4']

# スタティックルートを加えていく
ipv4.route_attr['10.10.10.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
ipv4.route_attr['10.10.20.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
ipv4.route_attr['10.10.30.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
ipv4.route_attr['10.10.40.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
ipv4.route_attr['10.10.50.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'

# これは必須
uut.add_feature(static_routing)

# ここで作ったコンフィグは辞書型
# {r1: {}}
cfgs = static_routing.build_config(apply=False)
pprint(str(cfgs[uut.name]))

# スタティックルートをデバイスに追加します
static_routing.build_config(apply=True)

# スタティックルートを削除する設定を作ります
cfgs = static_routing.build_unconfig(apply=False)
pprint(str(cfgs[uut.name]))

# スタティックルートをデバイスから消します
static_routing.build_unconfig(apply=True)

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()
