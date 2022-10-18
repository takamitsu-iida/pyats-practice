#!/usr/bin/env python

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

testbed = load('lab.yml')

uut = testbed.devices['uut']

for name, dev in testbed.devices.items():
    if dev.platform == 'CSR1000v':

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
