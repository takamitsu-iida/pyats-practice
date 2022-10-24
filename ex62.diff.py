#!/usr/bin/env python

#
# compare two ops objects
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html
#

# usage: ex62.diff.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

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

testbed = load(args.testbed)

uut = testbed.devices['uut']

uut.connect(via='console')

# learn routing table
pre_routing = uut.learn('routing')

# change static route
uut.configure('''
ip route 192.168.100.0 255.255.255.0 null 0
''')

# learn current routing table
post_routing = uut.learn('routing')

# revert static route
uut.configure('''
no ip route 192.168.100.0 255.255.255.0 null 0
''')

# disconnect
if uut.is_connected():
    uut.disconnect()

# from genie.utils.diff import Diff
# diff = Diff(pre_ospf, post_ospf)
# diff.findDiff()
# print(diff)

print('='*10)
print('WITHOUT EXCLUDE')
print('='*10)

diff = post_routing.diff(pre_routing)
diff.findDiff()
print(diff)

print('='*10)
print('WITH EXCLUDE')
print('='*10)

# routingではこれらを差分計算の対象から除外
exclude=['updated']

diff = post_routing.diff(pre_routing, exclude=exclude)
diff.findDiff
print(diff)
