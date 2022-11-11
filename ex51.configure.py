#!/usr/bin/env python

#
# configure using Genie Conf Object
#

# usage: ex51.configure.py [-h] [--testbed TESTBED]
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

# 設定できる機能はここで検索
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models
from genie.conf.base import Interface

# testbedファイルのなかでtopologyを記述してしまうと例外がでる
# File "src/pyats/topology/device.py", line 296, in pyats.topology.device.DeviceBase.add_interface
# pyats.topology.exceptions.DuplicateInterfaceError: Interface 'GigabitEthernet1' already exists on this device 'r1'.
# 設定変更する場合には、testbedファイルからtoplogyのセクションを消すこと

gig1 = Interface(device=uut, name='GigabitEthernet1')
gig2 = Interface(device=uut, name='GigabitEthernet2')
gig3 = Interface(device=uut, name='GigabitEthernet3')
gig4 = Interface(device=uut, name='GigabitEthernet4')
gig1.description = "configured by Genie Conf Object"
gig2.description = "configured by Genie Conf Object"
gig3.description = "configured by Genie Conf Object"
gig4.description = "configured by Genie Conf Object"

# verify config
print(gig1.build_config(apply=False))
print(gig2.build_config(apply=False))
print(gig3.build_config(apply=False))
print(gig4.build_config(apply=False))

# apply config
gig1.build_config(apply=True)
#gig2.build_config(apply=True)
#gig3.build_config(apply=True)
#gig4.build_config(apply=True)

# 注意！
# unconfigすると全てのインタフェース設定が消え、shutdownが打ち込まれる
# gig1.build_unconfig(apply=True)
# !
# default interface GigabitEthernet1
# interface GigabitEthernet1
#  shutdown
# !

# 特定の項目だけを消したい場合はattributeを付与する
# 複数項目を消したい場合はattributes={"switchport_enable": True, "enable": True}のように辞書型で渡す
gig1.build_unconfig(apply=True, attributes="description")

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()
