#!/usr/bin/env python

#
# show interfacesをパースして、CSV形式で保存する
#

# usage: ex21.parse_csv.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse
import sys
import os

from pprint import pprint
from jinja2 import Environment, FileSystemLoader

#
# overwrite standard telnetlib
#
def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

lib_dir = here('./lib')
if not lib_dir in sys.path:
  sys.path.insert(0, lib_dir)

import telnetlib

if telnetlib.MODIFIED_BY:
    print('modified telnetlib is loaded.')

# script args
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

# import Genie
from genie.testbed import load

log_dir = here('./log')
templates_dir = here('./templates')

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect
uut.connect(via='console')

# parse "show interfaces"
parsed = uut.parse('show interfaces')

# disconnect
if uut.is_connected():
    uut.disconnect()

# 辞書型を画面表示して内容を確認
pprint(parsed)

#
# CSVに加工して保存
#

# jinja2の環境設定
env = Environment(loader=FileSystemLoader(templates_dir))

# CSVテンプレートを取得
csv_template = env.get_template('show_interfaces.csv.j2')

# レンダリング
rendered = csv_template.render(parsed=parsed)

# 保存するファイル名
rendered_path = os.path.join(log_dir, f'ex21_{uut.hostname}_show_interfaces.csv')

# 保存
with open(rendered_path, 'w') as f:
    f.write(rendered)
    f.close()
