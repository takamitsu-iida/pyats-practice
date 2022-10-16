#!/usr/bin/env python

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

#
# execute command and parse the output
#

# Genieでパースできるコマンドはここで確認
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers

output = uut.parse('show version')

from pprint import pprint
pprint(output)
