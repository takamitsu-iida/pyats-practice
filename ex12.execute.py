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

# import Genie
from genie.testbed import load
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
try:
    uut.connect(via='console')
except (TimeoutError, ConnectionError) as e:
    print(e)
    sys.exit(1)

# execute command
try:
    output = uut.execute('show running-config')
except SubCommandFailure as e:
    print(e)

# disconnect from the uut
if uut.is_connected():
    uut.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
    uut.settings.POST_DISCONNECT_WAIT_SEC = 0
    uut.disconnect()

from pprint import pprint
pprint(output)
