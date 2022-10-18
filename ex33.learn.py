#!/usr/bin/env python

#
# 抽象的な機能名を指定して学習させる
#

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

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect
uut.connect(via='console')

# learn
output = uut.learn('config')

# disconnect
if uut.is_connected():
    uut.disconnect()

from pprint import pprint
pprint(output)
