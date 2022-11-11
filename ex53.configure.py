#!/usr/bin/env python

#
# configure ospf
#
# ドキュメントがないので使い方はソースコードを参照
# https://github.com/CiscoTestAutomation/genielibs/blob/master/pkgs/conf-pkg/src/genie/libs/conf/ospf/iosxe/tests/test_ospf.py

# usage: ex53.configure.py [-h] [--testbed TESTBED]
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

from genie.libs.conf.vrf import Vrf
from genie.libs.conf.interface import Interface
from genie.libs.conf.ospf import Ospf

# create Vrf objects
vrf0 = Vrf('default')

# create Interface object
gig1 = Interface(name='GigabitEthernet1')

# create Ospf object
ospf1 = Ospf()

# add feature to the device
uut.add_feature(ospf1)

# add configurations to vrf default
ospf1.device_attr[uut].vrf_attr[vrf0].instance = '1'
ospf1.device_attr[uut].vrf_attr[vrf0].router_id = '192.168.255.1'
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_cost = 10
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_type = 'point-to-point'

cfgs = ospf1.build_config(apply=False)

# cfgs = {r1: {...}}
pprint(str(cfgs[uut.name]))

# 装置に適用します
ospf1.build_config(apply=True)

# 注意！
# 引数なしでunconfigするとospfの設定がまるごと消える
# ospf1.build_unconfig(apply=True)

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()
