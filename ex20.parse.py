#!/usr/bin/env python

#
# 単体のコマンドをパースする
#

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect
uut.connect(via='console')

# parse "show version"
output = uut.parse('show version')

# disconnect
if uut.is_connected():
    uut.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
    uut.settings.POST_DISCONNECT_WAIT_SEC = 0
    uut.disconnect()

from pprint import pprint
pprint(output)
