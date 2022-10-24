#!/usr/bin/env python

#
# save and load ops object
#

import argparse
import os
import sys

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

# log directory and log file
log_dir = os.path.join(here('.'), 'log')
log_file = os.path.join(log_dir, 'r1_interface.data')

testbed = load(args.testbed)

uut = testbed.devices['uut']

uut.connect(via='console')

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

# disconnect
if uut.is_connected():
    uut.disconnect()

# save
with open(log_file, 'wb') as f:
    f.write(intf.pickle(intf))

# load
import pickle
with open(log_file, 'rb') as f:
    loaded = pickle.load(f)

diff = loaded.diff(intf)
diff.findDiff()
print(diff)
