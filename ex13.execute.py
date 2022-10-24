#!/usr/bin/env python

#
# execute list of show commands and save to a file.
#

import argparse
import sys
import os

#
# overwrite standard telnetlib
#
def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

if not here('./lib') in sys.path:
  sys.path.insert(0, here('./lib'))

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
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

# show commands
command_list = [
    'show version',
    'show cdp neighbors',
    'show ip ospf neighbor',
    'show ip route'
]

# log directory
log_dir = os.path.join(here('.'), 'log')

# create log_dir
os.makedirs(log_dir, exist_ok=True)

testbed = load(args.testbed)

for name, dev in testbed.devices.items():
    # テストベッド内のすべてのCSR1000vを対象に
    if dev.platform == 'CSR1000v':
        # ファイルをオープンしてログ取り開始
        log_path = os.path.join(log_dir, f'ex13_{name}.log')
        with open(log_path, 'w') as f:
            # connect
            try:
                dev.connect(via='console')
            except (TimeoutError, ConnectionError, SubCommandFailure) as e:
                f.write(str(e))
                continue

            # execute
            for cmd in command_list:
                try:
                    f.write('\n===\n')
                    f.write(cmd)
                    f.write('\n===\n')
                    f.write(dev.execute(cmd))
                    f.write('\n\n')
                except SubCommandFailure:
                    f.write(f'`{cmd}` invalid. Skipping.')

            # disconnect
            if dev.is_connected():
                dev.disconnect()
