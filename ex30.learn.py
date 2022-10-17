#!/usr/bin/env python

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

#
# 抽象的な機能名を指定して学習させる
#

# サポートしている機能名はここから探す
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models

# routing table

routing = uut.learn('routing')

from pprint import pprint
pprint(routing.info)
