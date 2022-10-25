#!/usr/bin/env python

#
# compare two ops objects
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html
#

# usage: ex61.diff.py [-h] [--testbed TESTBED]
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

# learn ospf state
pre_ospf = uut.learn('ospf')

# change ospf config
# cost 100 -> 10
uut.configure('''
interface Gig1
ip ospf cost 10
exit
''')

# learn current ospf state
post_ospf = uut.learn('ospf')

# revert ospf config
uut.configure('''
interface Gig1
ip ospf cost 100
exit
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

diff = post_ospf.diff(pre_ospf)
diff.findDiff()
print(diff)

print('='*10)
print('WITH EXCLUDE')
print('='*10)

# OSPFではこれらを差分計算の対象から除外
exclude = [
    'database',
    'dead_timer',
    'hello_timer',
    'statistics'
    ]

diff = post_ospf.diff(pre_ospf, exclude=exclude)
diff.findDiff
print(diff)
