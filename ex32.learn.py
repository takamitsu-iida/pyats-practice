#!/usr/bin/env python

#
# 抽象的な機能名を指定して学習させる
#

from pprint import pprint

# import Genie
from genie.testbed import load
from unicon.core.errors import TimeoutError, ConnectionError, SubCommandFailure

testbed = load('lab.yml')

learnt = {}
for name, dev in testbed.devices.items():
    if dev.type == 'Switch':
        try:
            # connect
            dev.connect(via='console')

            # learn
            learnt[name] = dev.learn('stp')

            # disconnect
            dev.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 1
            dev.settings.POST_DISCONNECT_WAIT_SEC = 1
            dev.disconnect()

        except (TimeoutError, ConnectionError, SubCommandFailure) as e:
            print(e)

for name, stp in learnt.items():
    print(name)
    pprint(stp.info)
