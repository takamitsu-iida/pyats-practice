#!/usr/bin/env python

#
# show interfacesをパースして、CSV形式で保存する
#

import sys
import os

from pprint import pprint

# import jinja2
from jinja2 import Environment, FileSystemLoader

# import Genie
from genie.testbed import load

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

log_dir = here('./log')
lib_dir = here('./lib')
templates_dir = here('./templates')

#
# overwrite standard telnetlib
#

if not lib_dir in sys.path:
  sys.path.insert(0, lib_dir)

import telnetlib

if telnetlib.MODIFIED_BY:
    print('modified telnetlib is loaded.')

#
# pyATS
#

testbed = load('lab.yml')

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
