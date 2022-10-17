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
print("modified telnetlib is loaded. DEBUG LEVEL is {}.".format(telnetlib.DEBUGLEVEL))

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

output = uut.learn('config')

from pprint import pprint
pprint(output)
