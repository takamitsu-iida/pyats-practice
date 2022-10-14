#!/usr/bin/env python

# Import Genie
from genie.conf import Genie

testbed = Genie.init('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

#
# コマンドを打ち込んでパースする
#

# Genieでパースできるコマンドはここで確認
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers

output = uut.parse('show version')

from pprint import pprint
pprint(output)
