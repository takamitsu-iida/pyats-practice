#!/usr/bin/env python

#
# save and load ops object
#

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

# log directory and log file
log_dir = os.path.join(here('.'), 'log')
log_file = os.path.join(log_dir, 'r1_interface.data')

# テストベッドをロードします
testbed = load(args.testbed)

# 名前（もしくはエイリアス）が'uut'になっている装置を取り出します（uut = unit under test）
uut = testbed.devices['uut']

# そのデバイスに接続します
uut.connect()

# 機種固有のInterfaceをインポートする場合
# from genie.libs.ops.interface.ios.interface import Interface
# from genie.libs.ops.interface.iosxr.interface import Interface
# from genie.libs.ops.interface.iosxe.interface import Interface

# 装置情報から自動で機種にあったInterfaceをロードする場合
from genie.ops.utils import get_ops
Interface = get_ops('interface', uut)
intf = Interface(device=uut)

# learn all interface
intf.learn()

# そのデバイスとの接続を切ります
if uut.is_connected():
    uut.disconnect()

# ファイルに保存します
with open(log_file, 'wb') as f:
    f.write(intf.pickle(intf))

# ファイルからロードします
import pickle
with open(log_file, 'rb') as f:
    loaded = pickle.load(f)

# ファイルに保存した情報と差分が無いことを確認します
diff = loaded.diff(intf)
diff.findDiff()
print(diff)
