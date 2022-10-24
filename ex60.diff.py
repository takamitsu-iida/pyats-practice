#!/usr/bin/env python

#
# compare two ops objects
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html
#

# usage: ex60.diff.py [-h] [--testbed TESTBED]
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
from genie.utils.diff import Diff

testbed = load(args.testbed)

uut = testbed.devices['uut']

uut.connect(via='console')

# learn configuration
pre_conf = uut.learn('config')

# change ospf config
# cost 100 -> 10
uut.configure('''
interface Gig1
ip ospf cost 10
exit
''')

# learn current config
post_conf = uut.learn('config')

# revert ospf config
uut.configure('''
interface Gig1
ip ospf cost 100
exit
''')

# disconnect
if uut.is_connected():
    uut.disconnect()

# generate diff
config_diff = Diff(pre_conf, post_conf)
config_diff.findDiff()
print(config_diff)
