#!/usr/bin/env python

#
# same as ex10.execute.py
#

import sys

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
    output = uut.execute('show version')
except SubCommandFailure as e:
    print(e)

# disconnect from the uut
if uut.is_connected():
    uut.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
    uut.settings.POST_DISCONNECT_WAIT_SEC = 0
    uut.disconnect()

# print output
from pprint import pprint
pprint(output)
