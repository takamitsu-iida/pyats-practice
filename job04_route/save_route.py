#!/usr/bin/env python

#
# 'routing'を学習してファイルに保存します
#

import os

# import Genie
from genie.testbed import load
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# pickle directory
pkl_dir = os.path.join(here('.'), 'pkl')

# create pkl_dir
os.makedirs(pkl_dir, exist_ok=True)

# load testbed
testbed = load('../lab.yml')

for name, dev in testbed.devices.items():
    # テストベッド内のすべてのCSR1000vを対象に
    if dev.platform != 'CSR1000v':
        continue

    # 保存ファイル名 routing.{name}.pickle
    log_path = os.path.join(pkl_dir, f'routing.{name}.pickle')

    # ファイルがあれば削除
    if os.path.exists(log_path):
        os.remove(log_path)

    try:
        # connect
        dev.connect(via='console')

        # learn routing table
        routing = dev.learn('routing')

        # disconnect
        if dev.is_connected():
            dev.disconnect()
    except (TimeoutError, ConnectionError, SubCommandFailure) as e:
        continue

    # save
    with open(log_path, 'wb') as f:
        f.write(routing.pickle(routing))
