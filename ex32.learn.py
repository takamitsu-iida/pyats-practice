#!/usr/bin/env python

#
# 抽象的な機能名を指定して学習させる
#

# サポートしている機能名はここから探す
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

learnt = {}
for name, dev in testbed.devices.items():
    if dev.type == 'Switch':
        dev.connect(via='console')
        learnt[name] = dev.learn('stp')

from pprint import pprint

for name, stp in learnt.items():
    print(name)
    pprint(stp.info)
