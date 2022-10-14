#!/usr/bin/env python

# Import Genie
from genie.conf import Genie

testbed = Genie.init('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

#
# コマンドを打ち込む
#
output = uut.execute('show version')

from pprint import pprint
pprint(output)
