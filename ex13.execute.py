#!/usr/bin/env python

#
# execute list of show commands and save to a file.
#

import argparse
import sys
import os

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

# 例外クラスをインポートします
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

# show commands
command_list = [
    'show version',
    'show cdp neighbors',
    'show ip ospf neighbor',
    'show ip route'
]

# ログを保存するディレクトリ
log_dir = os.path.join(here('.'), 'log')

# log_dirがなければ作ります
os.makedirs(log_dir, exist_ok=True)

# テストベッドをロードします
testbed = load(args.testbed)

for name, dev in testbed.devices.items():
    # テストベッド内のすべてのCSR1000vを対象に
    if dev.platform == 'csr1000v':
        # ファイルをオープンしてログ取り開始
        log_path = os.path.join(log_dir, f'ex13_{name}.log')
        with open(log_path, 'w') as f:
            # そのデバイスに接続します
            try:
                dev.connect()
            except (TimeoutError, ConnectionError, SubCommandFailure) as e:
                f.write(str(e))
                continue

            # コマンドリストから取り出して順番に投げ込みます
            for cmd in command_list:
                try:
                    f.write('\n===\n')
                    f.write(cmd)
                    f.write('\n===\n')
                    f.write(dev.execute(cmd))
                    f.write('\n\n')
                except SubCommandFailure:
                    f.write(f'`{cmd}` invalid. Skipping.')

            # そのデバイスとの接続を切ります
            if dev.is_connected():
                dev.disconnect()
