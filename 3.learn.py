#!/usr/bin/env python

# Import Genie
from genie.conf import Genie

testbed = Genie.init('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

#
# 抽象的な機能名を指定して学習させる
#

# 機能名はここから探す
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models

routing = uut.learn('routing')

from pprint import pprint
pprint(routing.info)
