#!/usr/bin/env python

#
# スイッチ系装置のshow interfaces statusをパースして、HTML形式で保存する
#

# usage: ex22.parse_html.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
import os

from pprint import pformat
from jinja2 import Environment, FileSystemLoader

# script args
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

log_dir = here('./log')
templates_dir = here('./templates')

#
# pyATS
#

# import Genie
from genie.testbed import load

testbed = load(args.testbed)

parsed = {}
for name, dev in testbed.devices.items():
    # typeが'switch'になっている全ての装置に対して接続
    if dev.type != 'switch':
        continue

    # connect
    dev.connect()

    # parse
    parsed[name] = dev.parse('show interfaces status')

    # disconnect
    dev.disconnect()

# 辞書型を画面表示して内容を確認
parsed_output = pformat(parsed)
print(parsed_output)

#
# HTMLに加工して保存
#

# jinja2の環境設定
env = Environment(loader=FileSystemLoader(templates_dir))

# HTMLテンプレートを取得
html_template = env.get_template('show_interfaces_status.html.j2')

# レンダリング
rendered = html_template.render(parsed=parsed, parsed_output=parsed_output)

# 保存するファイル名
rendered_path = os.path.join(log_dir, 'ex22.html')

# 保存
with open(rendered_path, 'w') as f:
    f.write(rendered)
    f.close()
