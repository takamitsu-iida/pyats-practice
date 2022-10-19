#!/usr/bin/env python

#
# ファイルに保存された'routing'をロードして表示します
#

import os
import pickle
from pprint import pprint

# import Genie
from genie.testbed import load

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# pickle directory
pkl_dir = os.path.join(here('.'), 'pkl')

# load testbed
testbed = load('../lab.yml')

for name, dev in testbed.devices.items():
    # テストベッド内のすべてのCSR1000vを対象に
    if dev.platform != 'CSR1000v':
        continue

    # ファイル名 routing.{name}.pickle
    log_path = os.path.join(pkl_dir, f'routing.{name}.pickle')

    assert os.path.exists(log_path), f'file not found, device: {name}'

    with open(log_path, 'rb') as f:
        loaded = pickle.load(f)

    print('='*10)
    print(name)
    print('='*10)
    pprint(loaded.info)
